"""
read_file_compressor.py — Compression helper for read_file tool output.

The read_file tool returns formatted strings with line numbers:
    [File: foo.py | 100 lines | 5.2KB | showing lines 1-50]

    1: import os
    2: # comment
    3: def main():

However, when stored in the DB via json.dumps(), string results get
JSON-quoted (e.g., '"[File: ...]\\n\\n1: ..."').  The RTK filter pipeline
splits on "\n" and won't work correctly on JSON-quoted strings.

This module provides a single utility that:
1. De-JSONs the content if it appears JSON-wrapped
2. Delegates to the standard RTK compressor_registry for filtering

Language-aware comment stripping is handled by the read_file.toml filter.

Usage:
    from backend.token_compressor.read_file_compressor import compress_read_file_result
    compressed = compress_read_file_result(content)
"""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)


def compress_read_file_result(content: str) -> str:
    """Compress a read_file tool result, handling JSON-wrapped content.

    If *content* is a JSON-quoted string (as stored by json.dumps),
    unwrap it before passing to the RTK compressor.  Otherwise pass
    through as-is.

    Args:
        content: Raw content from DB (may be JSON-quoted).

    Returns:
        Compressed output, or original content on failure (fail-open).
    """
    raw = _unwrap_json(content)

    try:
        from backend.token_compressor.compressor_registry import get_registry
        reg = get_registry()
        compressed = reg.compress("read_file", 0, raw)
        # Only use if the compressor actually changed something
        if compressed != raw:
            return compressed
    except Exception:
        logger.debug(
            "read_file_compressor: RTK compressor unavailable, "
            "returning original",
            exc_info=True,
        )

    return content


def _unwrap_json(content: str) -> str:
    """If content is a JSON-quoted string, unwrap it.

    Example: '"Hello\\nWorld"' -> 'Hello\nWorld'
    """
    if content.startswith('"') and content.endswith('"'):
        try:
            unquoted = json.loads(content)
            if isinstance(unquoted, str):
                return unquoted
        except (json.JSONDecodeError, TypeError):
            pass
    return content
