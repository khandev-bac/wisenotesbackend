from langchain_text_splitters import MarkdownTextSplitter


def chunk_md(mdtext: str, source_id: str, user_id: str):
    splitter = MarkdownTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = splitter.create_documents([mdtext])
    chunks = []
    for doc in docs:
        chunks.append(
            {
                "text": doc.page_content,
                "metadata": {"source_id": source_id, "user_id": user_id},
            }
        )
    return chunks
