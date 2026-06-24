from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_web_documents(urls):
    documents = []
    for url in urls:
        loader = WebBaseLoader(url)
        docs = loader.load()
        for doc in docs:
            doc.metadata["source_url"] = url

        documents.extend(docs)
    return documents

def chunk_documents(documents):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500,chunk_overlap=50,separators = ["\n\n", "\n", ".", " "])
    chunks = splitter.split_documents(documents)
    print('length of total chunks ',len(chunks))
    return chunks

def ingest_urls(urls: list[str]):
    documents = load_web_documents(urls)
    chunks = chunk_documents(documents)
    return chunks