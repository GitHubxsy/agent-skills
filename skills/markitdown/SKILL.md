---
name: markitdown
description: Convert files, documents, and URLs into clean Markdown for LLM consumption with Microsoft's MarkItDown. Use for extracting or reading PDF, Word, PowerPoint, Excel, HTML, CSV, JSON, XML, EPUB, ZIP, Outlook, image, audio, or YouTube content; converting one file or a folder; ingesting documents; preparing content for summarization, search, RAG, or other analysis; troubleshooting MarkItDown dependencies; using plugins, OCR, transcription, or Azure extraction. Trigger on requests such as "convert to Markdown," "extract text," "read this document into text," "ingest these files," or "turn this PDF/deck/spreadsheet into text," even when MarkItDown is not named. Do not use to author or edit Office/PDF files; use the format-specific skill for those tasks.
---

# MarkItDown

Convert source material into Markdown optimized for language-model and text-analysis workflows. Preserve useful structure such as headings, lists, tables, links, and metadata; do not promise page-faithful visual reproduction.

## Choose a workflow

- Convert one local file or supported URL: use the `markitdown` CLI.
- Convert several local files reproducibly: use `scripts/convert.py`.
- Integrate conversion into an application or pass streams: use the Python API.
- Need OCR for embedded images: install and enable `markitdown-ocr`, then configure an LLM client.
- Need scanned-document layout, structured fields, audio/video, or higher extraction quality: consider Azure Content Understanding.
- Need cloud layout extraction for documents only: consider Azure Document Intelligence.

## Install safely

Require Python 3.10 or newer. Prefer an isolated environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install 'markitdown[all]'
```

Install only required extras when dependency size matters, for example:

```bash
python -m pip install 'markitdown[pdf,docx,pptx,xlsx]'
```

Available extras include `pptx`, `docx`, `xlsx`, `xls`, `pdf`, `outlook`, `az-doc-intel`, `az-content-understanding`, `audio-transcription`, and `youtube-transcription`.

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

## Plugins and OCR

Plugins are disabled by default. Inspect installed plugins before enabling them:

```bash
markitdown --list-plugins
markitdown --use-plugins document.pdf -o document.md
```

For OCR of images embedded in PDF, DOCX, PPTX, or XLSX, install `markitdown-ocr` and an OpenAI-compatible client, then pass `enable_plugins=True`, `llm_client`, and `llm_model` to `MarkItDown`. Treat plugin code and model-bound document contents as trusted data flows.

## Azure conversion

Use Azure Content Understanding only when its extra quality or modality support justifies a billable cloud call:

```bash
markitdown report.pdf --use-cu --cu-endpoint "$AZURE_CONTENT_UNDERSTANDING_ENDPOINT" -o report.md
```

It can route documents, images, audio, and video, and can serialize analyzer fields as YAML front matter. Restrict routing by file type in Python when only some formats should incur cloud processing.

Use Azure Document Intelligence for cloud document layout extraction:

```bash
markitdown report.pdf -d -e "$AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT" -o report.md
```

Never print or commit credentials. Confirm the user's permission before sending confidential material to Azure or an LLM provider.

## Verify the result

After conversion:

1. Confirm the output exists, is non-empty, and is valid UTF-8 Markdown.
2. Inspect headings, tables, links, and representative sections against the source.
3. Report unsupported or weakly extracted content instead of silently claiming completeness.
4. For scanned PDFs or image-heavy documents, check whether OCR is required.
5. Keep the original source unless the user explicitly authorizes deletion.

## Security boundaries

MarkItDown performs file and network I/O with the current process privileges. Treat source paths, URLs, archives, plugins, and generated output as untrusted when their provenance is unknown. Avoid broad filesystem privileges, do not enable plugins implicitly, and use the narrowest conversion method available.

MarkItDown produces analysis-oriented Markdown, not a high-fidelity replacement for the original document. Use a format-specific document skill when layout preservation, editing, tracked changes, or pixel-accurate rendering matters.
