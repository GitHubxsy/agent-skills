#!/usr/bin/env python3
"""Batch-convert local files or directory trees to Markdown."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

try:
    from markitdown import MarkItDown
except ImportError as exc:
    raise SystemExit(
        "MarkItDown is not installed. Install only the extras you need, for example: "
        "python -m pip install 'markitdown[pdf,docx,pptx,xlsx]'"
    ) from exc


UNSUPPORTED_MEDIA_EXTENSIONS = {".mp3", ".mp4", ".m4a", ".wav"}
STANDALONE_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
DIRECT_VISION_EXTENSIONS = STANDALONE_IMAGE_EXTENSIONS | {".pptx"}
OCR_DOCUMENT_EXTENSIONS = {".pdf", ".docx", ".xlsx"}
LOOPBACK_HOSTS = {"127.0.0.1", "localhost", "::1"}


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
        "--local-vision-model",
        help="Local vision model for images and images embedded in documents",
    )
    parser.add_argument(
        "--local-llm-base-url",
        help=(
            "Loopback OpenAI-compatible endpoint; overrides "
            "MARKITDOWN_LLM_BASE_URL"
        ),
    )
    parser.add_argument(
        "--image-prompt",
        default=(
            "Extract all visible text, preserving its reading order, and describe "
            "important non-text visual information."
        ),
        help="Prompt sent to the local vision model",
    )
    return parser.parse_args()


def create_local_llm_client(base_url: str, api_key: str):
    parsed = urlparse(base_url)
    if parsed.scheme not in {"http", "https"} or parsed.hostname not in LOOPBACK_HOSTS:
        raise ValueError("local LLM endpoint must use localhost or a loopback IP address")
    try:
        import httpx
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "install the local client with: python -m pip install openai"
        ) from exc
    return OpenAI(
        base_url=base_url,
        api_key=api_key,
        http_client=httpx.Client(trust_env=False),
    )


def main() -> int:
    args = parse_args()
    missing = [path for path in args.inputs if not path.exists()]
    if missing:
        for path in missing:
            print(f"error: input does not exist: {path}", file=sys.stderr)
        return 2

    args.output_dir.mkdir(parents=True, exist_ok=True)

    sources: list[tuple[Path, Path]] = []
    for item in args.inputs:
        if item.is_file():
            sources.append((item, Path(item.name)))
            continue
        for source in sorted(path for path in item.rglob("*") if path.is_file()):
            sources.append((source, Path(item.name) / source.relative_to(item)))

    vision_options = {}
    if args.local_vision_model:
        base_url = (
            args.local_llm_base_url
            or os.environ.get("MARKITDOWN_LLM_BASE_URL")
            or "http://127.0.0.1:11434/v1"
        )
        api_key = os.environ.get("MARKITDOWN_LLM_API_KEY") or "local-only"
        try:
            vision_options.update(
                llm_client=create_local_llm_client(base_url, api_key),
                llm_model=args.local_vision_model,
                llm_prompt=args.image_prompt,
            )
        except (RuntimeError, ValueError) as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2

    converter = MarkItDown(enable_plugins=False)
    needs_embedded_image_ocr = bool(vision_options) and any(
        source.suffix.lower() in OCR_DOCUMENT_EXTENSIONS
        for source, _ in sources
    )
    if needs_embedded_image_ocr:
        try:
            from markitdown_ocr import (
                DocxConverterWithOCR,
                LLMVisionOCRService,
                PdfConverterWithOCR,
                XlsxConverterWithOCR,
            )
        except ImportError as exc:
            print(
                "error: install embedded-image support with: "
                "python -m pip install markitdown-ocr",
                file=sys.stderr,
            )
            return 2
        ocr_service = LLMVisionOCRService(
            client=vision_options["llm_client"],
            model=vision_options["llm_model"],
            default_prompt=vision_options["llm_prompt"],
        )
        converter.register_converter(
            PdfConverterWithOCR(ocr_service=ocr_service), priority=-1.0
        )
        converter.register_converter(
            DocxConverterWithOCR(ocr_service=ocr_service), priority=-1.0
        )
        converter.register_converter(
            XlsxConverterWithOCR(ocr_service=ocr_service), priority=-1.0
        )

    failures = 0

    for source, relative in sources:
        if source.suffix.lower() in UNSUPPORTED_MEDIA_EXTENSIONS:
            print(f"error: audio/video is not supported: {source}", file=sys.stderr)
            failures += 1
            continue
        destination = args.output_dir / relative.parent / f"{relative.name}.md"
        if destination.exists() and not args.overwrite:
            print(f"skip: {destination} exists (use --overwrite)", file=sys.stderr)
            failures += 1
            continue

        try:
            conversion_options = (
                vision_options
                if source.suffix.lower() in DIRECT_VISION_EXTENSIONS
                else {}
            )
            result = converter.convert_local(source, **conversion_options)
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
