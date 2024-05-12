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
import speech_recognition as sr
from textblob import TextBlob

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

def find_pdf_filename():
    """
    Retrieve the filename of a single PDF in the KnowledgeBase directory.
    """

    # Get a list of PDF files in the KnowledgeBase directory
    pdf_files = [f for f in os.listdir(DOCS_DIR) if f.endswith(".pdf")]

    # Raise an error if no PDF file is found
    if not pdf_files:
        raise FileNotFoundError("No PDF found in KnowledgeBase.")
    
    # Raise an error if multiple PDF files are found
    if len(pdf_files) > 1:
        raise ValueError("Multiple PDFs found. Ensure only one is present.")
    
    return pdf_files[0]


def load_pdf_documents() -> List[Document]:
    """
    Load and return documents from a PDF file in the KnowledgeBase directory.
    """

    print(">>> Loading PDF document...")
    filename = find_pdf_filename()
    pdf_path = os.path.join(DOCS_DIR, filename)
    pdf_documents = PyPDFLoader(pdf_path).load()
    cprint(f">>> Loaded, pages: {len(pdf_documents)}", "green")

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
    Create and store embeddings in a vectorstore from document chunks.
    """

    # Create a vectorstore from the document chunks
    vector_store = Chroma.from_documents(
        docs, embedding=embeddings, collection_name=DB_COLLECTION, persist_directory=VECTOR_STORE_PATH)

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
            embedding_function=embeddings, collection_name=DB_COLLECTION, persist_directory=VECTOR_STORE_PATH).as_retriever(search_kwargs={"k": 3})
        
    except ValueError as e:
        if str(e) == f"Collection {DB_COLLECTION} does not exist.":
            documents = load_pdf_documents()
            chunks = split_documents(documents)

            # Create a new vectorstore and retriever
            retriever = create_embeddings_store(embeddings, chunks).as_retriever(search_kwargs={"k": 3})
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

def recognize_speech():
    """
    Recognize speech input from the user using the microphone.
    Returns the recognized text if successful, None otherwise.
    """

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=None)
        except sr.WaitTimeoutError:
            print("No speech detected. Timeout reached.")
            return None

    try:
        text = recognizer.recognize_google(audio)
        print(f"You said: {text}")
        return text
    except sr.UnknownValueError:
        print("Sorry, I could not understand your speech.")
    except sr.RequestError as e:
        print(f"Error: {e}")

def analyze_sentiment(text):
    """
    Analyze the sentiment of the given text using TextBlob.
    Returns the sentiment label (Positive, Negative, or Neutral) and the sentiment score.
    """

    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "Positive", sentiment
    elif sentiment < 0:
        return "Negative", sentiment
    else:
        return "Neutral", sentiment

def store_negative_sentiment(user_input, response, sentiment_score):
    """
    Store the user input, chatbot response, and sentiment score in a file when the sentiment is negative.
    """

    with open("negative_sentiments.txt", "a") as file:
        file.write(f"User Input: {user_input}\n")
        file.write(f"Response: {response}\n")
        file.write(f"Sentiment Score: {sentiment_score}\n")
        file.write("---\n")

def execute_chat_chain(chain: Runnable) -> None:
    """
    Execute the chat chain interactively, allowing the user to choose between text input and speech input.
    Analyze the sentiment of the user input and store negative sentiments in a file.
    """

    while True:
        print("How would you like to communicate with the bot?")
        print("1. Type\n2. Speak")
        input_mode = input("Enter the number associated with your preferred method or type 'quit', 'q' or 'exit' to exit: ")
        if input_mode.lower() in ["quit", "q", "exit"]:
            break
        if input_mode.lower() not in ["1", "2"]:
            print("Invalid input mode. Please select 1 for'chat' or 2 for 'voice'.")
            continue

        if input_mode == "1":
            user_input = input("> Question: ")
        elif input_mode == "2":
            user_input = recognize_speech()
            if user_input is None:
                continue

        sentiment, sentiment_score = analyze_sentiment(user_input)
        print(f"Sentiment: {sentiment} (Score: {sentiment_score:.2f})")

        # Start the timer
        start_time = time.time()
        
        # Invoke the retrieval chain with the user input
        response = chain.invoke({"input": user_input})
        
        # Calculate the response time
        response_time = time.time() - start_time

        print("\n> Answer:")
        print("\n" + response["answer"], end="\n\n")

        # Print the response time
        print(f"Response time: {response_time:.2f} seconds")

        if sentiment == "Negative":
            store_negative_sentiment(user_input, response["answer"], sentiment_score)

def main() -> None:
    """
    Main function to set up the chatbot and start the interaction.
    """

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    llm = ChatGroq(temperature=LLM_TEMP, model_name=LLM_MODEL)
    chat_chain = configure_chat_chain(embeddings, llm)
    execute_chat_chain(chat_chain)

if __name__ == "__main__":
    main()