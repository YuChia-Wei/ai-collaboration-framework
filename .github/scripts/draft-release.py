#!/usr/bin/env python3
"""Create an owned GitHub Draft Release and verify exact assets; never publish."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

sys.path.insert(0, str(Path(__file__).absolute().parent))
from release_common import WORKFLOW, document, encoded, oid, require, sha, tag_name, verify_bundle

MARKER = "<!-- aicf-draft-delivery-v1:"


class SafeRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        require(urllib.parse.urlsplit(newurl).scheme == "https", "insecure provider redirect")
        request = super().redirect_request(req, fp, code, msg, headers, newurl)
        if request:
            request.remove_header("Authorization")
        return request


class GitHub:
    def __init__(self, repository, token):
        require(re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository), "repository identity")
        require(bool(token), "GITHUB_TOKEN required")
        self.repository = repository
        self.token = token
        self.prefix = "https://api.github.com/repos/" + repository
        self.opener = urllib.request.build_opener(SafeRedirect())

    def request(self, method, path, data=None, binary=False):
        url = path if path.startswith("https://") else self.prefix + path
        parsed = urllib.parse.urlsplit(url)
        require(parsed.hostname in ("api.github.com", "uploads.github.com") and parsed.scheme == "https", "provider endpoint")
        headers = {"Authorization": "Bearer " + self.token, "X-GitHub-Api-Version": "2022-11-28",
                   "Accept": "application/octet-stream" if binary else "application/vnd.github+json",
                   "User-Agent": "aicf-source-draft-delivery"}
        if isinstance(data, dict):
            data = encoded(data)
            headers["Content-Type"] = "application/json"
        elif data is not None:
            headers["Content-Type"] = "application/octet-stream"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with self.opener.open(request, timeout=90) as response:
                raw = response.read(256 * 1024 * 1024 + 1)
                require(len(raw) <= 256 * 1024 * 1024, "provider response budget")
        except urllib.error.HTTPError as exc:
            # Do not expose response headers, secrets or arbitrary provider payloads.
            raise ValueError(f"GitHub {method} failed with HTTP {exc.code}; preserve partial state and inspect run receipt; no credential fallback") from None
        return raw if binary else document(raw)

    def pages(self, path):
        rows = []
        for page in range(1, 101):
            values = self.request("GET", path + f"?per_page=100&page={page}")
            require(isinstance(values, list), "provider list shape")
            rows.extend(values)
            if len(values) < 100:
                return rows
        raise ValueError("provider pagination budget exceeded")


def remote_source(api, source):
    tag = tag_name(source["tag"])
    ref = api.request("GET", "/git/ref/tags/" + urllib.parse.quote(tag, safe=""))
    obj = ref["object"]
    require(ref["ref"] == "refs/tags/" + tag and obj["type"] == "tag"
            and obj["sha"] == source["tag_object"], "provider tag object drift")
    annotated = api.request("GET", "/git/tags/" + oid(source["tag_object"]))
    require(annotated["sha"] == source["tag_object"] and annotated["tag"] == tag
            and annotated["object"]["type"] == "commit"
            and annotated["object"]["sha"] == source["commit"], "provider tag/source drift")


def marker(manifest, manifest_raw):
    return MARKER + json.dumps({"workflow": WORKFLOW, "source": manifest["source"],
        "manifest_sha256": sha(manifest_raw)}, sort_keys=True, separators=(",", ":")) + " -->"


def owned(release, manifest, manifest_raw):
    require(release["draft"] is True, "published release is immutable; refusing all writes")
    require(release["tag_name"] == manifest["source"]["tag"], "release tag mismatch")
    body = release.get("body") or ""
    require(body.count(MARKER) == 1 and marker(manifest, manifest_raw) in body,
            "draft ownership/source/admitted bytes mismatch; use original run assets, never replace a draft")
    return body


def generic_body(manifest, manifest_raw):
    source, archive = manifest["source"], manifest["archive"]
    return (
        marker(manifest, manifest_raw) + "\n\n"
        f"Draft delivery for **{source['tag']}**.\n\n"
        f"- Source commit: {source['commit']}\n"
        f"- Annotated tag object: {source['tag_object']}\n"
        f"- Catalog: {manifest['catalog_identity']}\n"
        f"- Archive: {archive['name']} ({archive['size']} bytes; SHA-256 {archive['sha256']})\n"
        f"- Build run: {manifest['provenance']['run_id']}, attempt {manifest['provenance']['run_attempt']}\n\n"
        "The generic package contains the full catalog, Engine 2, independent engine pin and content hashes. "
        "Archive verification does not establish tests, native/runtime acceptance or publication.\n\n"
        "Owner handoff: ask Codex or ChatGPT to author release notes from the prior-tag..source range "
        "and merged PR/Issue evidence, preserving this ownership marker. Then review and explicitly publish "
        "using GitHub. Notes can be edited without rebuilding assets.\n"
    )


def deliver(api, directory, manifest, receipt):
    source = manifest["source"]
    require(source["tag"] is not None, "snapshots cannot create releases")
    require(manifest["provenance"]["workflow"] == WORKFLOW, "draft requires release workflow provenance")
    manifest_raw = (directory / "release-manifest.json").read_bytes()
    remote_source(api, source)
    matches = [r for r in api.pages("/releases") if r["tag_name"] == source["tag"]]
    require(len(matches) <= 1, "ambiguous duplicate releases for tag")
    files = {name: (directory / name).read_bytes() for name in
             ("release-manifest.json", manifest["archive"]["name"], manifest["archive"]["name"] + ".sha256")}
    release = matches[0] if matches else None
    if release:
        body = owned(release, manifest, manifest_raw)
    else:
        remote_source(api, source)
        # Existing tag was read back. Omit target_commitish: never request tag creation.
        release = api.request("POST", "/releases", {
            "tag_name": source["tag"], "name": f"AI Collaboration Framework {source['tag']}",
            "body": generic_body(manifest, manifest_raw), "draft": True,
            "prerelease": "-" in manifest["version"].split("+")[0], "generate_release_notes": False})
        receipt["created_release_id"] = release["id"]
        body = owned(release, manifest, manifest_raw)
    release_id = release["id"]
    require(type(release_id) is int and release_id > 0, "provider release ID")
    receipt["release_id"] = release_id

    def read_release():
        current = api.request("GET", f"/releases/{release_id}")
        owned(current, manifest, manifest_raw)
        # Concurrent human edits are preserved; the writer never PATCHes body/title.
        return current

    read_release()
    assets = api.pages(f"/releases/{release_id}/assets")
    asset_names = [a["name"] for a in assets]
    require(len(asset_names) == len(set(asset_names)) and set(asset_names) <= set(files), "unexpected/duplicate draft assets")
    present = {}
    # Preflight every existing byte before adding any missing asset.
    for asset in assets:
        require(asset["state"] == "uploaded" and asset["size"] == len(files[asset["name"]]), "partial or mismatching draft asset; retain original artifacts")
        data = api.request("GET", f"/releases/assets/{asset['id']}", binary=True)
        require(data == files[asset["name"]], "mismatching draft asset bytes; no overwrite permitted")
        present[asset["name"]] = asset
    receipt["verified_existing_assets"] = sorted(present)
    for name, raw in files.items():
        if name in present:
            continue
        remote_source(api, source)
        read_release()
        upload = "https://uploads.github.com/repos/" + api.repository + f"/releases/{release_id}/assets?name=" + urllib.parse.quote(name, safe="")
        asset = api.request("POST", upload, raw)
        require(asset["name"] == name and asset["state"] == "uploaded" and asset["size"] == len(raw), "upload acknowledgement mismatch")
        receipt.setdefault("uploaded_assets", []).append(name)
    remote_source(api, source)
    final = read_release()
    final_assets = api.pages(f"/releases/{release_id}/assets")
    require(sorted(a["name"] for a in final_assets) == sorted(files), "final draft asset set mismatch")
    verified = []
    for asset in final_assets:
        raw = api.request("GET", f"/releases/assets/{asset['id']}", binary=True)
        require(asset["state"] == "uploaded" and asset["size"] == len(files[asset["name"]])
                and raw == files[asset["name"]], "final provider asset bytes mismatch")
        verified.append({"name": asset["name"], "id": asset["id"], "size": len(raw), "sha256": sha(raw)})
    receipt.update({"outcome": "draft-ready", "url": final["html_url"], "assets": sorted(verified, key=lambda r: r["name"]),
                    "body_written": not bool(matches), "existing_body_preserved": bool(matches),
                    "publication": "not-performed", "tests": "not-run"})
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--expected-tooling-commit", required=True)
    parser.add_argument("--expected-run-id", required=True)
    parser.add_argument("--expected-build-attempt", required=True)
    parser.add_argument("--expected-tag", required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args = parser.parse_args()
    receipt = {"schema": "framework-draft-delivery/1", "outcome": "failed",
               "started_at": datetime.now(timezone.utc).isoformat()}
    try:
        manifest = verify_bundle(args.assets)
        require(manifest["source"]["tag"] == tag_name(args.expected_tag), "event/manifest tag mismatch")
        prov = manifest["provenance"]
        require(prov["repository"] == args.repository and prov["run_id"] == args.expected_run_id
                and prov["tooling_commit"] == oid(args.expected_tooling_commit)
                and prov["workflow_commit"] == args.expected_tooling_commit
                and prov["run_attempt"] == args.expected_build_attempt, "workflow/run/manifest mismatch")
        receipt["source"] = manifest["source"]
        receipt["manifest_sha256"] = sha((args.assets / "release-manifest.json").read_bytes())
        api = GitHub(args.repository, os.environ.get("GITHUB_TOKEN", ""))
        deliver(api, args.assets, manifest, receipt)
        return 0
    except (ValueError, KeyError, TypeError, OSError, zipfile.BadZipFile) as exc:
        receipt["reason"] = str(exc)
        receipt["next_action"] = ("Retain this receipt and the original successful build artifact. Rerun failed writer jobs with "
            "those exact bytes. A full rebuild has new receipt bytes and must not replace admitted draft assets. "
            "If an upload is partial/starter or ownership differs, owner reconciliation is required. Never broaden credentials.")
        return 1
    finally:
        receipt["completed_at"] = datetime.now(timezone.utc).isoformat()
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_bytes(encoded(receipt))
        print(encoded(receipt).decode(), end="")


if __name__ == "__main__":
    raise SystemExit(main())
