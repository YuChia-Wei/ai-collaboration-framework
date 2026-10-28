"""Bounded, persisted exact-version read proofs. This module performs no IO."""
from __future__ import annotations

import base64

from . import source_contract as c
from .contracts import decode_json, require


def load(connection, proof_id, check_configuration=True):
    c.native_id(proof_id)
    row = connection.execute("SELECT value FROM source_read_proofs WHERE id=?", (proof_id,)).fetchone()
    require(row, "not_found", "Read proof is absent.")
    proof = c.parse(bytes(row[0]))
    if check_configuration:
        from .source_config import current
        require(current(connection, proof["workflow_id"])["configuration_revision"] == proof["configuration_revision"],
                "configuration_conflict", "Read token belongs to an earlier configuration; prepare a new read.")
    return proof


def plan(connection, proof):
    from .source_store import snapshot
    row, manifest = snapshot(connection, proof["snapshot_id"])
    if proof["target"] is None:
        return []
    target = proof["target"]
    common = {"service_contract_version": c.NATIVE_PROFILE, "schema_version": "1.0", "project_ref": target["project_ref"]}
    payload = {"source_id": target["source_id"], "workflow_id": manifest["workflow"]["id"], "source_revision": row[4]}
    output = [{**common, "query": "replica.read", "payload": payload}]
    # Empty manifests still require one explicit, complete zero-item page.
    for offset in range(0, max(1, len(manifest["files"])), 50):
        output.append({**common, "query": "replica.manifest", "payload": {**payload, "offset": offset, "limit": 50}})
    for file in manifest["files"]:
        for index in range((file["size"] + c.CHUNK - 1) // c.CHUNK):
            output.append({**common, "query": "replica.file.chunk", "payload": {**payload, "path": file["path"], "index": index}})
    return output


def next_step(connection, proof):
    steps = plan(connection, proof)
    completed = connection.execute("SELECT count(*) FROM source_read_evidence WHERE proof_id=?", (proof["proof_id"],)).fetchone()[0]
    require(completed <= len(steps), "integrity_error", "Read proof contains extra evidence.")
    if completed == len(steps):
        return {"proof_id": proof["proof_id"], "read_state": "complete", "step_count": len(steps)}
    query = steps[completed]
    c.validate("query", query)
    return {"proof_id": proof["proof_id"], "read_state": "pending", "step_index": completed, "step_count": len(steps),
            "tool_name": "source_v1_" + query["query"].replace(".", "_"), "request": query}


def prepare(connection, request):
    from .source_config import current, latest
    from .source_store import synchronization, snapshot
    config = current(connection, request["workflow_id"])
    require(c.integer(request["expected_configuration_revision"]) == config["configuration_revision"], "configuration_conflict", "Workflow configuration changed.")
    cut = latest(connection, request["workflow_id"])
    purpose = "selection" if "binding_id" in request else "read"
    selected = {"kind": "replica", "binding_id": request["binding_id"]} if purpose == "selection" else config["read_source"]
    key, target, generation = cut, None, None
    if selected["kind"] == "replica":
        c.native_id(selected["binding_id"])
        require(selected["binding_id"] in config["bindings"], "not_found", "Selected replica binding is absent.")
        binding = config["bindings"][selected["binding_id"]]
        generation, target = binding["generation_id"], binding["target"]
        if purpose == "read":
            # Read a known activated immutable version, never infer remote
            # order from a native digest or silently substitute local bytes.
            known = set()
            for (raw,) in connection.execute("SELECT value FROM source_read_proofs"):
                prior = c.parse(bytes(raw))
                if prior["workflow_id"] == request["workflow_id"] and prior["generation_id"] == generation:
                    count = connection.execute("SELECT count(*) FROM source_read_evidence WHERE proof_id=?", (prior["proof_id"],)).fetchone()[0]
                    if count == len(plan(connection, prior)):
                        known.add(prior["snapshot_id"])
            candidates = connection.execute("SELECT i.snapshot_id FROM replica_intents i JOIN source_snapshots s ON s.id=i.snapshot_id WHERE i.binding_id=? AND s.kind='native-workflow' AND s.workflow_id=? ORDER BY s.sequence DESC", (generation, request["workflow_id"])).fetchall()
            key = next((item[0] for item in candidates if item[0] in known or any(t["binding_id"] == generation and t["state"] == "complete"
                        for t in synchronization(connection, item[0])["targets"])), None)
            require(key, "source_unavailable", "The selected replica has no proven complete version; no fallback was used.")
    row, manifest = snapshot(connection, key)
    proof_id = "read-" + c.digest(c.canonical(request))[7:]
    proof = {"proof_id": proof_id, "workflow_id": request["workflow_id"], "configuration_revision": config["configuration_revision"],
             "purpose": purpose, "binding_id": selected.get("binding_id"), "generation_id": generation, "target": target,
             "snapshot_id": key, "source_revision": row[4], "manifest_hash": c.digest(c.canonical(manifest)), "authority_cut": cut}
    connection.execute("INSERT INTO source_read_proofs VALUES(?,?)", (proof_id, c.canonical(proof)))
    return {**next_step(connection, proof), "read_token": proof}


def verify_evidence(connection, proof, index, native, prior_revision=None):
    from .source_store import snapshot
    row, manifest = snapshot(connection, proof["snapshot_id"])
    steps = plan(connection, proof)
    c.integer(index, 0)
    require(index < len(steps), "invalid_input", "Read step is outside the prepared proof.")
    query = steps[index]
    selector = {"replica.read": "result_replica_read", "replica.manifest": "result_replica_manifest", "replica.file.chunk": "result_replica_file_chunk"}[query["query"]]
    c.validate(selector, native)
    require(native["project_ref"] == proof["target"]["project_ref"] and native["source_id"] == proof["target"]["source_id"]
            and native["workflow_id"] == manifest["workflow"]["id"] and native["source_revision"] == row[4]
            and native["manifest_hash"] == proof["manifest_hash"] and native["complete"] is True,
            "source_mismatch", "Read response differs from the pinned project/source/workflow/version/hash.")
    require(prior_revision is None or native["revision"] == prior_revision, "source_mismatch", "Provider activation revision changed across read pages.")
    if query["query"] == "replica.read":
        require(native["metadata"] == {"source": manifest["source"], "workflow": manifest["workflow"]}
                and native["file_count"] == len(manifest["files"]) and native["total_bytes"] == sum(file["size"] for file in manifest["files"]),
                "integrity_error", "Remote header does not describe the complete expected manifest.")
    elif query["query"] == "replica.manifest":
        offset = query["payload"]["offset"]
        require(native["offset"] == offset and native["total"] == len(manifest["files"])
                and native["files"] == manifest["files"][offset:offset + 50]
                and native["has_more"] == (offset + 50 < len(manifest["files"])),
                "integrity_error", "Manifest page is incomplete, reordered or inconsistent.")
    else:
        selected = query["payload"]
        require(native["path"] == selected["path"] and native["index"] == selected["index"], "source_mismatch", "Chunk selector changed.")
        chunk = connection.execute("SELECT b.hash,b.data FROM source_chunks sc JOIN source_blobs b ON b.hash=sc.hash WHERE sc.snapshot_id=? AND sc.path=? AND sc.chunk_index=?", (proof["snapshot_id"], selected["path"], selected["index"])).fetchone()
        raw = c.decode_chunk(native["content_base64"])
        require(chunk and native["chunk_hash"] == chunk[0] and c.digest(raw) == chunk[0] and raw == bytes(chunk[1]),
                "integrity_error", "Remote chunk bytes differ from the complete immutable source.")
    return native["revision"]


def accept(connection, request):
    proof = load(connection, request["proof_id"])
    index = c.integer(request["step_index"], 0)
    completed = connection.execute("SELECT count(*) FROM source_read_evidence WHERE proof_id=?", (proof["proof_id"],)).fetchone()[0]
    require(index == completed, "read_step_conflict", "Accept the next exact read step, or replay its original operation.")
    require(not isinstance(request["mcp_result"], dict) or not request["mcp_result"].get("isError", False), "source_unavailable", "Selected source returned a transport error; no fallback was used.")
    native = c.mcp_value(request["mcp_result"])
    prior = connection.execute("SELECT value FROM source_read_evidence WHERE proof_id=? AND step_index=0", (proof["proof_id"],)).fetchone()
    verify_evidence(connection, proof, index, native, c.parse(bytes(prior[0]))["revision"] if prior else None)
    connection.execute("INSERT INTO source_read_evidence VALUES(?,?,?)", (proof["proof_id"], index, c.canonical(native)))
    return next_step(connection, proof)


def proven(connection, proof_id):
    proof = load(connection, proof_id)
    require(next_step(connection, proof)["read_state"] == "complete", "source_incomplete", "Every pinned header, manifest page and chunk must be verified.")
    return proof


def result(connection, request):
    from .source_config import latest
    from .source_store import snapshot
    proof = proven(connection, request["proof_id"])
    row, manifest = snapshot(connection, proof["snapshot_id"])
    if request["operation"] == "read-chunk":
        c.path(request["path"])
        index = c.integer(request["index"], 0)
        if proof["target"] is not None:
            for (raw,) in connection.execute("SELECT value FROM source_read_evidence WHERE proof_id=? ORDER BY step_index", (proof["proof_id"],)):
                native = c.parse(bytes(raw))
                if native.get("path") == request["path"] and native.get("index") == index:
                    return {"read_token": proof, "chunk": native}
            require(False, "not_found", "Selected source proof has no such chunk.")
        chunk = connection.execute("SELECT b.hash,b.data FROM source_chunks sc JOIN source_blobs b ON b.hash=sc.hash WHERE sc.snapshot_id=? AND sc.path=? AND sc.chunk_index=?", (row[1], request["path"], index)).fetchone()
        require(chunk, "not_found", "Selected local source has no such chunk.")
        return {"read_token": proof, "chunk": {"path": request["path"], "index": index, "chunk_hash": chunk[0], "content_base64": base64.b64encode(bytes(chunk[1])).decode("ascii")}}
    provider_revision = None
    if proof["target"] is None:
        raw = b"".join(bytes(item[0]) for item in connection.execute("SELECT b.data FROM source_chunks sc JOIN source_blobs b ON b.hash=sc.hash WHERE sc.snapshot_id=? AND sc.path='_native/state.json' ORDER BY sc.chunk_index", (row[1],)))
    else:
        evidence = [c.parse(bytes(item[0])) for item in connection.execute("SELECT value FROM source_read_evidence WHERE proof_id=? ORDER BY step_index", (proof["proof_id"],))]
        provider_revision = evidence[0]["revision"]
        raw = b"".join(c.decode_chunk(item["content_base64"]) for item in evidence if item.get("path") == "_native/state.json")
    return {"read_state": "complete", "read_token": proof, "manifest": manifest, "native_state": decode_json(raw),
            "logical_revision": row[4], "native_state_revision": manifest["source"]["native_revision"],
            "provider_revision": provider_revision, "freshness": "current" if row[1] == latest(connection, proof["workflow_id"]) else "behind",
            "authority_cut": latest(connection, proof["workflow_id"])}
