"""Portable artifact mechanics; adapters retain parsing and semantic authority.

This module does not select YAML/JSON dialects, accepted versions, record states,
validation authority or evidence custody. Callers supply their mapping policy.
"""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Iterator
from typing import Any

import yaml


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def construct_unique_mapping(
    loader: yaml.SafeLoader, node: yaml.MappingNode, *,
    flatten: bool, deep: bool = False,
    key_error: Callable[[Any, bool], Exception],
) -> dict:
    """Keep duplicate detection and string keys shared, with explicit merge policy.

    The adapter supplies its existing diagnostic/exception boundary. Flattening
    is allowed only by the execution dialect; authoring rejects graph tokens.
    Values are constructed after key checks to preserve failure ordering.
    """
    if flatten:
        loader.flatten_mapping(node)
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise key_error(key, False)
        if key in result:
            raise key_error(key, True)
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


def yaml_tokens(text: str, *, refuse_comments: bool = False) -> Iterator[yaml.tokens.Token]:
    """Scan decoded YAML, optionally refusing real comments before reserialization.

    Scalar spans own literal hashes. Block scalar header comments are inside
    their scalar token, so the header needs a separate check. No global loader
    or resolver is modified, and malformed YAML remains a scanner error.
    """
    cursor = 0
    for token in yaml.scan(text):
        if refuse_comments:
            start, end = token.start_mark.index, token.end_mark.index
            comment = "#" in text[cursor:start]
            if isinstance(token, yaml.tokens.ScalarToken) and token.style in ("|", ">"):
                header = re.split(r"[\r\n\x85\u2028\u2029]", text[start:end], maxsplit=1)[0]
                comment |= "#" in header
            if comment:
                raise yaml.YAMLError("YAML comments cannot be rewritten losslessly; move comments to prose or use a reviewed manual edit")
            cursor = max(cursor, end)
        yield token
    if refuse_comments and "#" in text[cursor:]:
        raise yaml.YAMLError("YAML comments cannot be rewritten losslessly; move comments to prose or use a reviewed manual edit")
