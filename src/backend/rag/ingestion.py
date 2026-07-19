from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.backend.logging.logger import logger

def load_web_documents(loader, urls):
    documents = []
    for url in urls:
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_url"] = url

        documents.extend(docs)
    return documents


def chunk_documents(documents):
    logger.info('[chunk_documents] Entering chunk documents')
    splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50,separators = ["\n\n", "\n", ".", " "])
    chunks = splitter.split_documents(documents)
    logger.debug('[chunk_documents] length of total chunks ',len(chunks), ' for document ',documents[0].metadata['source_url'] )
    return chunks

def chunk_documents_with_filter(documents):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", ".", " "]
    )
    chunks = splitter.split_documents(documents)
    logger.debug(f'[chunk_documents_with_filter] Total chunks before filter: {len(chunks)}')

    # Filter out citation chunks — they start with ↑ or contain only references
    filtered = [
        c for c in chunks
        if len(c.page_content.strip()) > 100          # remove very short chunks
        and not c.page_content.strip().startswith("↑") # remove footnotes
        and "Retrieved" not in c.page_content[:50]     # remove citation lines
    ]

    logger.info(f'[chunk_documents_with_filter] Total chunks after filter: {len(filtered)}')
    return filtered


def ingest_urls(urls: list[str],filter = False):
    print(f'[ingest_urls]Inside ingest_urls')
    loader = WebBaseLoader(urls)
    documents = load_web_documents(loader,urls)
    print('[ingest_urls]Finished loading documents')
    if  filter:
        return chunk_documents_with_filter(documents)
    print('[ingest_urls]Finished chunking documents')
    return chunk_documents(documents)