---
name: markitdown
description: Convert files, documents, images, and URLs into clean Markdown for LLM consumption with Microsoft's MarkItDown. Use for extracting or reading PDF, Word, PowerPoint, Excel, HTML, CSV, JSON, XML, EPUB, ZIP, Outlook, or image content; converting one file or a folder; ingesting documents into a knowledge base; preparing content for summarization, search, RAG, or other analysis; using a local OpenAI-compatible vision model for JPG/PNG descriptions; or troubleshooting MarkItDown dependencies. Trigger on requests such as "convert to Markdown," "extract text," "read this document into text," "ingest these files," or "turn this PDF/deck/spreadsheet/image into text," even when MarkItDown is not named. Audio and video transcription are intentionally unsupported. Do not use to author or edit Office/PDF files; use the format-specific skill for those tasks.
---

# MarkItDown

Convert source material into Markdown optimized for language-model and text-analysis workflows. Preserve useful structure such as headings, lists, tables, links, and metadata; do not promise page-faithful visual reproduction.

## Choose a workflow

- Convert one local file or supported URL: use the `markitdown` CLI.
- Convert several local files reproducibly: use `scripts/convert.py`.
- Integrate conversion into an application or pass streams: use the Python API.
- Convert JPG/PNG images: run the bundled script with a local OpenAI-compatible vision model.
- Reject audio and video inputs; this Skill does not transcribe them.

## Install safely

Require Python 3.10 or newer. Prefer an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'markitdown[pdf,docx,pptx,xlsx,xls,outlook]' openai
```

Install only required extras when dependency size matters, for example:

```bash
python -m pip install 'markitdown[pdf,docx,pptx,xlsx]'
```

Do not install `markitdown[all]` for this Skill because it includes audio-transcription dependencies. Install only the document extras required by the task.

Do not alter a user's project environment without permission. Reuse an existing compatible environment when present; otherwise explain or create an isolated one within the task scope.

## Convert content

For one input:

```bash
markitdown report.pdf -o report.md
markitdown https://example.com/page -o page.md
cat report.pdf | markitdown > report.md
```

For multiple local inputs, run:

```bash
python scripts/convert.py file.pdf slides.pptx notes.docx --output-dir markdown
python scripts/convert.py source-folder --output-dir markdown
```

The script recursively converts directories and preserves their relative structure. It preserves each source extension in the output name (`file.pdf.md`) to avoid collisions. Add `--overwrite` only when replacing existing outputs is intended. Add `--use-plugins` only for trusted, installed plugins.

## Describe images with a local vision model

Start a local server that exposes an OpenAI-compatible chat-completions API, such as Ollama, LM Studio, or vLLM. The model must support image input.

For Ollama, start the service and make sure a vision model is available, then run:

```bash
python scripts/convert.py diagram.png \
  --local-vision-model <vision-model> \
  --output-dir markdown
```

The default endpoint is `http://127.0.0.1:11434/v1`. Override it only for another loopback endpoint:

```bash
python scripts/convert.py photos \
  --local-vision-model <vision-model> \
  --local-llm-base-url http://localhost:1234/v1 \
  --image-prompt "Describe the image and transcribe visible text." \
  --output-dir markdown
```

The script rejects non-loopback LLM endpoints. It sends image bytes only to the local service and does not configure a cloud API key. Without `--local-vision-model`, JPG/PNG conversion is limited to locally extractable metadata and may produce no Markdown.

For application code:

```python
from markitdown import MarkItDown

converter = MarkItDown(enable_plugins=False)
result = converter.convert("report.xlsx")
markdown = result.markdown
```

`result.text_content` remains a soft-deprecated alias for `result.markdown`.

Choose the narrowest API that fits:

| Method | Use for |
| --- | --- |
| `convert(source)` | Trusted path, URL, or stream when permissive dispatch is useful |
| `convert_local(path)` | Local files only; safest default for on-disk content |
| `convert_uri(uri)` / `convert_url(url)` | Remote content, including supported YouTube URLs |
| `convert_stream(fileobj)` | An already-open binary stream; provide `StreamInfo` when the type is ambiguous |
| `convert_response(response)` | A `requests.Response` fetched under caller-controlled network policy |

When bytes have no useful filename, pass a hint:

```python
from markitdown import MarkItDown, StreamInfo

with open("mystery.bin", "rb") as stream:
    result = MarkItDown().convert_stream(
        stream,
        stream_info=StreamInfo(extension=".pdf", mimetype="application/pdf"),
    )
```

## Handle failures

Catch `MarkItDownException` when conversion errors need programmatic handling. Its subclasses include `MissingDependencyException`, `UnsupportedFormatException`, and `FileConversionException`. A recognized format with a missing parser can surface as a `FileConversionException` wrapping the dependency error, so inspect the full message and conversion attempts instead of catching only `MissingDependencyException`.

Install the exact extra named in a missing-dependency message and retry. If installation is unavailable, fall back to a dedicated format skill rather than abandoning the extraction task.

## Plugins

Plugins are disabled by default. Inspect installed plugins before enabling them:

```bash
markitdown --list-plugins
markitdown --use-plugins document.pdf -o document.md
```

Do not enable cloud-backed plugins. Inspect any plugin before enabling it and confirm that it performs no external network calls when local-only processing is required.

## Verify the result

After conversion:

1. Confirm the output exists, is non-empty, and is valid UTF-8 Markdown.
2. Inspect headings, tables, links, and representative sections against the source.
3. Report unsupported or weakly extracted content instead of silently claiming completeness.
4. For images, confirm the local vision model returned a useful description and visible text.
5. Keep the original source unless the user explicitly authorizes deletion.

## Security boundaries

MarkItDown performs file and network I/O with the current process privileges. Treat source paths, URLs, archives, plugins, and generated output as untrusted when their provenance is unknown. Avoid broad filesystem privileges, do not enable plugins implicitly, and use the narrowest conversion method available. Keep the local LLM bound to loopback unless the user explicitly designs and authorizes a different trusted deployment.

Do not process audio or video with this Skill. Route those inputs to a separately reviewed local transcription workflow if support is added later.

MarkItDown produces analysis-oriented Markdown, not a high-fidelity replacement for the original document. Use a format-specific document skill when layout preservation, editing, tracked changes, or pixel-accurate rendering matters.
