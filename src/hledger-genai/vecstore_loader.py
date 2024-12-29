from langchain_google_genai.embeddings import GoogleGenerativeAIEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
import glob

def prepare_vectorstore(vectorstore_path: str, document_path_glob: list[str]):
    vector_store = Chroma(
        embedding_function=GoogleGenerativeAIEmbeddings(model="models/text-embedding-004"),
        persist_directory=vectorstore_path,  # Where to save data locally, remove if not necessary
    )
    for doc_path in document_path_glob:
        glob_path = glob.glob(doc_path, recursive=True)
        for path in glob_path:
            loader = TextLoader(path)
            data = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(separators=["\n\n"])
            splits = text_splitter.split_documents(data)
            vector_store.add_documents(splits)

def load_vectorstore(vectorstore_path: str):
    vector_store = Chroma(
        embedding_function=GoogleGenerativeAIEmbeddings(model="models/text-embedding-004"),
        persist_directory=vectorstore_path,  # Where to save data locally, remove if not necessary
    )
    return vector_store