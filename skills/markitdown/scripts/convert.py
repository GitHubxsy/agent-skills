#!/usr/bin/env python3
"""Batch-convert local files or directory trees to Markdown."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from markitdown import MarkItDown
except ImportError as exc:
    raise SystemExit(
        "MarkItDown is not installed. Run: python -m pip install 'markitdown[all]'"
    ) from exc


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert one or more local files to Markdown."
    )
    parser.add_argument("inputs", nargs="+", type=Path, help="Local files or directories")
    parser.add_argument(
        "-o", "--output-dir", type=Path, default=Path("markdown"), help="Output directory"
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Replace existing Markdown outputs"
    )
    parser.add_argument(
        "--use-plugins", action="store_true", help="Enable installed MarkItDown plugins"
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    missing = [path for path in args.inputs if not path.exists()]
    if missing:
        for path in missing:
            print(f"error: input does not exist: {path}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)
    converter = MarkItDown(enable_plugins=args.use_plugins)
    failures = 0

    sources: list[tuple[Path, Path]] = []
    for item in args.inputs:
        if item.is_file():
            sources.append((item, Path(item.name)))
            continue
        for source in sorted(path for path in item.rglob("*") if path.is_file()):
            sources.append((source, Path(item.name) / source.relative_to(item)))

    for source, relative in sources:
        destination = args.output_dir / relative.parent / f"{relative.name}.md"
        if destination.exists() and not args.overwrite:
            print(f"skip: {destination} exists (use --overwrite)", file=sys.stderr)
            failures += 1
            continue

        try:
            result = converter.convert_local(source)
            content = result.markdown
            if not content.strip():
                raise ValueError("converter returned empty Markdown")
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(content, encoding="utf-8")
            print(f"converted: {source} -> {destination}")
        except Exception as exc:  # Preserve progress when one batch item fails.
            print(f"error: {source}: {exc}", file=sys.stderr)
            failures += 1

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
