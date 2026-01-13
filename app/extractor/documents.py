from docling.document_converter import DocumentConverter

from app.helper import download_file


def convert_doc_md(file_url: str) -> str:
    local_path = download_file(file_url)
    try:
        converter = DocumentConverter()
        result = converter.convert(str(local_path))
        markdown = result.document.export_to_markdown()
        return markdown
    finally:
        local_path.unlink(missing_ok=True)
