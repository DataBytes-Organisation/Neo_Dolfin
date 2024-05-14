import os
import time
from typing import List
import chromadb
from dotenv import load_dotenv
from langchain.chains.combine_documents.stuff import create_stuff_documents_chain
from langchain.chains.retrieval import create_retrieval_chain
from langchain.docstore.document import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_core.runnables import Runnable
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from termcolor import cprint
from transformers import AutoTokenizer
import re

# Constants for configuration
EMBEDDING_MODEL = "hkunlp/instructor-large"  # Embedding model used for document retrieval
LLM_MODEL = "llama3-70b-8192"  # Language model used for generating responses
LLM_TEMP = 0.1  # Temperature setting for the language model
CHUNK_SIZE = 8192  # Max chunk size for embedding model

# Define directories for storing documents and vector data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOCS_DIR = os.path.join(BASE_DIR, "KnowledgeBase")

VECTOR_STORE_PATH = os.path.join(BASE_DIR, "VectorStore")
os.makedirs(VECTOR_STORE_PATH, exist_ok=True)

MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Load environment variables from .env file
load_dotenv()

DB_COLLECTION = "collection1" 

def find_pdf_filenames():
    """
    Retrieve a list of PDF filenames in the KnowledgeBase directory.
    """

    # Get a list of PDF files in the KnowledgeBase directory
    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]

    return pdf_files


def load_pdf_document(pdf: str) -> List[Document]:
    """
    Load and return documents from a single PDF file.
    """

    pdf_path = os.path.join(DOCS_DIR, pdf)
    pdf_documents = PyPDFLoader(pdf_path).load()

    return pdf_documents

def split_documents(docs: List[Document]) -> List[Document]:
    """
    Split documents into smaller chunks of predefined size for processing.
    """

    # Load the tokenizer for the embedding model
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL, cache_dir=MODEL_DIR)
    # Create a text splitter using the tokenizer
    splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer, chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_SIZE // 50)
    
    print(">>> Splitting documents...")
    # Split the documents into chunks
    document_chunks = splitter.split_documents(docs)

    cprint(f">>> Split into {len(document_chunks)} chunks.", "green")

    return document_chunks

def create_embeddings_store(embeddings: HuggingFaceEmbeddings, docs: List[Document]) -> Chroma:
    """
    Create and store embeddings in a vectorstore from all documents.
    """

    # Concatenate all documents into a single document
    all_text = "\n\n".join(str(doc) for doc in docs)

    cprint(">>> Creating vector store...", "yellow")
    # Create a vectorstore from all documents
    vector_store = Chroma.from_documents(
        [Document(text=all_text, page_content=all_text)], 
        embedding=embeddings, 
        collection_name=DB_COLLECTION, 
        persist_directory=VECTOR_STORE_PATH
    )

    cprint(">>> Vectorstore created.", "green")

    return vector_store




def get_document_retriever(embeddings: HuggingFaceEmbeddings) -> VectorStoreRetriever:
    """
    Retrieve or create a document vectorstore for embedding retrieval.
    """

    # Create a ChromaDB client for the vectorstore
    db = chromadb.PersistentClient(VECTOR_STORE_PATH)

    try:
        # Check if the collection exists in the vectorstore
        db.get_collection(DB_COLLECTION)
        # Create a retriever using the existing collection
        retriever = Chroma(
            embedding_function=embeddings, collection_name=DB_COLLECTION, persist_directory=VECTOR_STORE_PATH).as_retriever(search_kwargs={"k": 1})
        
    except ValueError as e:
        if str(e) == f"Collection {DB_COLLECTION} does not exist.":
            documents = load_pdf_document()
            chunks = split_documents(documents)

            # Create a new vectorstore and retriever
            retriever = create_embeddings_store(embeddings, chunks).as_retriever(search_kwargs={"k": 1})
        else:
            raise e

    return retriever

def configure_chat_chain(embeddings: HuggingFaceEmbeddings, llm: ChatGroq) -> Runnable:
    """
    Configure the Retrieval-Augmented Generation (RAG) chain for the chatbot.
    """

    prompt_template = """
    You are a helpful financial well-being and open banking website application assistant, you will use the provided context to answer user questions.
    Read the given context which has QnA for FAQs so you will look uo for the best possible answer for the asked question before answering questions and think step by step. If you can not answer a user question based on 
    the provided context, inform the user. Do not use any other information for answering user. Provide a detailed answer to the question and never mwntion what is inside the document that you are using to answering the 
    questions because you are a working bot for Dolfin's website.
    To help guide you in the dataset, the column labels are:
    Date,Transaction Description,Debit,Credit,Balance,Category 1,Category 2,Category 3,DR/CR
    <context>
    {context}
    </context>

    Question: {input}

    """

    prompt = ChatPromptTemplate.from_template(prompt_template)
    docs_chain = create_stuff_documents_chain(llm=llm, prompt=prompt)
    retriever = get_document_retriever(embeddings)
    retrieval_chain = create_retrieval_chain(retriever, docs_chain)

    return retrieval_chain

def execute_chat_chain(chain: Runnable) -> None:
    """
    Run the chat chain interactively to handle user queries.
    """

    while True:
        # Get user input
        user_input = input("> Question: ")
        # Exit the loop if the user inputs "quit", or "exit"
        if user_input.lower() in ["quit", "exit"]:
            break

        # Extract month from user input
        month_regex = r"(january|february|march|april|may|june|july|august|september|october|november|december)"
        month_match = re.search(month_regex, user_input, re.IGNORECASE)
        if month_match:
            month = month_match.group(0).capitalize()

            # Check if a PDF file with the month's name exists
            pdf_filename = f"{month}.pdf"
            pdf_path = os.path.join(DOCS_DIR, pdf_filename)
            if os.path.exists(pdf_path):
                # Load PDF file and extract the relevant data
                pdf_documents = PyPDFLoader(pdf_path).load()
                chunked_docs = split_documents(pdf_documents)
                context = ""
                for chunk in chunked_docs:
                    context += str(chunk)

                # Invoke the retrieval chain with the user input and context
                response = chain.invoke({"input": user_input, "context": context})

                print("\n> Answer:")
                print("\n" + response["answer"], end="\n\n")
            else:
                print(f"No PDF file found for {month}.")
        else:
            # Invoke the retrieval chain with the user input (no month in msg)
            response = chain.invoke({"input": user_input})

            print("\n> Answer:")
            print("\n" + response["answer"], end="\n\n")

def main() -> None:
    """
    Main function to set up the chatbot and start the interaction.
    """

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    llm = ChatGroq(temperature=LLM_TEMP, model_name=LLM_MODEL)

    # Find all PDF files in the KnowledgeBase directory
    pdfs = find_pdf_filenames()

    documents = []
    for pdf in pdfs:
        documents.extend(load_pdf_document(pdf))

    # Create vector store for all documents
    vector_store = create_embeddings_store(embeddings, documents)

    # Configure the chat chain
    chat_chain = configure_chat_chain(embeddings, llm)

    # Execute the chat chain
    execute_chat_chain(chat_chain)

if __name__ == "__main__":
    main()

