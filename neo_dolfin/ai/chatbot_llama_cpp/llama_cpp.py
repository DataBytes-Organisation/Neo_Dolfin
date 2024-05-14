import os
import logging
import torch
import sys
from langchain_community.llms import LlamaCpp
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings, HuggingFaceEmbeddings
from langchain_community.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.llms import HuggingFacePipeline
from langchain_community.document_loaders import CSVLoader, PDFMinerLoader, TextLoader, UnstructuredExcelLoader, Docx2txtLoader
from langchain_community.document_loaders import UnstructuredFileLoader, UnstructuredMarkdownLoader, UnstructuredHTMLLoader
from langchain.chains import RetrievalQA
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler 
from langchain.callbacks.manager import CallbackManager
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from chromadb.config import Settings
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from langchain.docstore.document import Document
from langchain.text_splitter import Language, RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma
from textblob import TextBlob
import speech_recognition as sr
import time

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
import csv
from termcolor import cprint
from datetime import datetime
from huggingface_hub import hf_hub_download
from transformers import AutoModelForCausalLM, AutoTokenizer, LlamaForCausalLM, LlamaTokenizer, BitsAndBytesConfig
from transformers import (
    GenerationConfig,
    pipeline,
)

# Define paths
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
DOCUMENTS_DIR = f"{ROOT_DIR}/KnowledgeBase"
VECTORSTORE_DIR = os.path.join(ROOT_DIR, "VectorStore")
MODELS_DIR = os.path.join(ROOT_DIR, "models")

# Create directories if they don't exist
os.makedirs(VECTORSTORE_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

# Threads and processing settings
NUM_INGEST_THREADS = os.cpu_count() or 8
CHUNK_SIZE = 4096
MAX_CHUNK_OVERLAP = 200
MAX_TOKENS = CHUNK_SIZE

# GPU settings
NUM_GPU_LAYERS = 100
BATCH_SIZE = 512

# Chroma database settings
CHROMA_SETTINGS = Settings(
    anonymized_telemetry=False,
    is_persistent=True,
)

# Document loaders map
DOC_LOADER_MAP = {
    ".html": UnstructuredHTMLLoader,
    ".txt": TextLoader,
    ".md": UnstructuredMarkdownLoader,
    ".pdf": UnstructuredFileLoader,
    ".csv": CSVLoader,
    ".xls": UnstructuredExcelLoader,
    ".xlsx": UnstructuredExcelLoader,
    ".docx": Docx2txtLoader,
    ".doc": Docx2txtLoader,
}

# Embedding and model settings
EMBEDDINGS_MODEL_NAME = "hkunlp/instructor-large"  
# EMBEDDINGS_MODEL_NAME = "all-MiniLM-L6-v2"
LLM_MODEL_ID = "TheBloke/Llama-2-7b-Chat-GGUF"
LLM_MODEL_BASENAME = "llama-2-7b-chat.Q4_K_M.gguf"

def write_log(log_entry):
    """
    Write a log entry to the log file and print it to the console.
    """
    with open("ingest.log", "a") as log_file:
        log_file.write(log_entry + "\n")
        print(log_entry + "\n")

def load_document(file_path: str) -> Document:
    """
    Load a single document from the given file path.
    """
    try:
        file_extension = os.path.splitext(file_path)[1]
        loader_class = DOC_LOADER_MAP.get(file_extension)
        if loader_class:
            write_log(f"{file_path} loaded.")
            loader = loader_class(file_path)
        else:
            write_log(f"{file_path} has an undefined document type.")
            raise ValueError("Undefined document type")
        return loader.load()[0]
    except Exception as e:
        write_log(f"Error loading {file_path}: \n{e}")
        return None
    
def load_documents_batch(file_paths):
    """
    Load a batch of documents using multithreading.
    """
    logging.info("Loading document batch")
    with ThreadPoolExecutor(len(file_paths)) as executor:
        futures = [executor.submit(load_document, path) for path in file_paths]
        if futures is None:
            write_log(f"{file_paths} failed to submit")
            return None
        else:
            documents = [future.result() for future in futures]
            return documents, file_paths

def load_documents(documents_dir: str) -> list[Document]:
    """
    Load all documents from the given directory using multiprocessing.
    """
    file_paths = []
    for root, _, files in os.walk(documents_dir):
        for file_name in files:
            print(f"Importing: {file_name}")
            file_extension = os.path.splitext(file_name)[1]
            file_path = os.path.join(root, file_name)
            if file_extension in DOC_LOADER_MAP.keys():
                file_paths.append(file_path)

    num_workers = min(NUM_INGEST_THREADS, max(len(file_paths), 1))
    batch_size = round(len(file_paths) / num_workers)
    all_documents = []
    with ProcessPoolExecutor(num_workers) as executor:
        futures = []
        for i in range(0, len(file_paths), batch_size):
            batch_paths = file_paths[i : (i + batch_size)]
            try:
                future = executor.submit(load_documents_batch, batch_paths)
            except Exception as e:
                write_log(f"Executor task failed: {e}")
                future = None
            if future is not None:
                futures.append(future)
        for future in as_completed(futures):
            try:
                batch_documents, _ = future.result()
                all_documents.extend(batch_documents)
            except Exception as e:
                write_log(f"Exception: {e}")

    return all_documents

def split_documents(documents: list[Document]) -> tuple[list[Document], list[Document]]:
    """
    Split the documents into text documents and code documents.
    """
    text_documents = []
    code_documents = []
    for doc in documents:
        if doc is not None:
            file_extension = os.path.splitext(doc.metadata["source"])[1]
            if file_extension == ".py":
                code_documents.append(doc)
            else:
                text_documents.append(doc)
    return text_documents, code_documents

def ingest_documents():
    """
    Ingest documents from the source directory, split them into chunks, and store them in the vectorstore.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logging.info(f"Loading documents from {DOCUMENTS_DIR}")
    documents = load_documents(DOCUMENTS_DIR)
    text_docs, code_docs = split_documents(documents)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=MAX_CHUNK_OVERLAP)
    code_splitter = RecursiveCharacterTextSplitter.from_language(
        language=Language.PYTHON, chunk_size=CHUNK_SIZE - 120, chunk_overlap=MAX_CHUNK_OVERLAP
    )
    text_chunks = text_splitter.split_documents(text_docs)
    code_chunks = code_splitter.split_documents(code_docs)
    chunks = text_chunks + code_chunks
    logging.info(f"Loaded {len(documents)} documents from {DOCUMENTS_DIR}")
    logging.info(f"Split into {len(chunks)} chunks")

    embeddings = get_embeddings(device)
    logging.info(f"Loaded embeddings from {EMBEDDINGS_MODEL_NAME}")

    vectorstore = Chroma.from_documents(
        chunks,
        embeddings,
        persist_directory=VECTORSTORE_DIR,
        client_settings=CHROMA_SETTINGS,
    )

# System prompt for the language model
SYSTEM_PROMPT = """You are a helpful financial well-being and open banking website application assistant. Use the provided context to answer user questions.
The context contains FAQs, so look for the best possible answer before responding. Think step by step.
If you cannot answer a question based on the provided context, inform the user. Do not use any information outside the given context.
Provide a detailed answer to the question."""

def get_prompt_template(system_prompt=SYSTEM_PROMPT, prompt_type=None, include_history=False):
    """
    Get the prompt template based on the prompt type and whether to include conversation history.
    """
    if prompt_type == "llama":
        B_INST, E_INST = "[INST]", "[/INST]"
        B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
        FULL_SYSTEM_PROMPT = B_SYS + system_prompt + E_SYS
        if include_history:
            INSTRUCTION = """
            Context: {history} \n {context}
            User: {question}"""
            FULL_PROMPT = B_INST + FULL_SYSTEM_PROMPT + INSTRUCTION + E_INST
            prompt = PromptTemplate(input_variables=["history", "context", "question"], template=FULL_PROMPT)
        else:
            INSTRUCTION = """
            Context: {context}
            User: {question}"""
            FULL_PROMPT = B_INST + FULL_SYSTEM_PROMPT + INSTRUCTION + E_INST
            prompt = PromptTemplate(input_variables=["context", "question"], template=FULL_PROMPT)

    memory = ConversationBufferMemory(input_key="question", memory_key="history")        
    return prompt, memory

def load_quant_model(model_id, model_basename, device, logging):
    """
    Load a quantized model using LlamaCpp.
    """
    try:
        logging.info("Using LlamaCpp for GGUF/GGML quantized models")
        model_path = hf_hub_download(
            repo_id=model_id,
            filename=model_basename,
            resume_download=True,
            cache_dir=MODELS_DIR,
        )
        kwargs = {
            "model_path": model_path,
            "n_ctx": CHUNK_SIZE,
            "max_tokens": MAX_TOKENS,
            "n_batch": BATCH_SIZE,
        }
        if device.lower() == "mps":
            kwargs["n_gpu_layers"] = 1
        if device.lower() == "cuda":
            kwargs["n_gpu_layers"] = NUM_GPU_LAYERS

        return LlamaCpp(**kwargs)
    except TypeError:
        if "ggml" in model_basename:
            logging.info("If using GGML model, LLAMA-CPP dropped support. Use GGUF instead.")
        return None

def load_full_model(model_id, model_basename, device, logging):
    """
    Load a full model using AutoModelForCausalLM and LlamaForCausalLM.
    """
    if device.lower() in ["mps", "cpu"]:
        logging.info("Using LlamaTokenizer")
        tokenizer = LlamaTokenizer.from_pretrained(model_id, cache_dir=MODELS_DIR)
        model = LlamaForCausalLM.from_pretrained(model_id, cache_dir=MODELS_DIR)
    else:
        logging.info("Using AutoModelForCausalLM for full models")
        tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=MODELS_DIR)
        logging.info("Tokenizer loaded")
        bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16
                )
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map="auto",
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            cache_dir=MODELS_DIR,
            trust_remote_code=True,
            quantization_config=bnb_config
        )
        model.tie_weights()
    return model, tokenizer

def get_embeddings(device="cuda"):
    """
    Get the embeddings model based on the specified embeddings model name.
    """
    if "bge" in EMBEDDINGS_MODEL_NAME:
        return HuggingFaceBgeEmbeddings(
            model_name=EMBEDDINGS_MODEL_NAME,
            model_kwargs={"device": device},
            query_instruction="Represent this text for relevant passage retrieval:",
        )
    else:
        return HuggingFaceEmbeddings(
            model_name=EMBEDDINGS_MODEL_NAME,
            model_kwargs={"device": device},
        )

def load_llm(device, model_id, model_basename=None, LOGGING=logging):
    """
    Load the language model (LLM) based on the specified model ID and basename.
    """
    if model_basename is not None:
        if ".gguf" in model_basename.lower():
            llm = load_quant_model(model_id, model_basename, device, LOGGING)
            return llm
        elif ".ggml" in model_basename.lower():
            model, tokenizer = load_quant_model(model_id, model_basename, device, LOGGING)
    else:
        model, tokenizer = load_full_model(model_id, model_basename, device, LOGGING)

    generation_config = GenerationConfig.from_pretrained(model_id)

    generate_text = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_length=MAX_TOKENS,
        temperature=0.2,
        repetition_penalty=1.15,
        generation_config=generation_config,
    )

    local_llm = HuggingFacePipeline(pipeline=generate_text)
    logging.info("Local LLM loaded")

    return local_llm

def create_qa_chain(device, prompt_type="llama"):
    """
    Create a question-answering chain using the loaded embeddings, vectorstore, and language model.
    """
    embeddings = get_embeddings(device)
    vectorstore = Chroma(persist_directory=VECTORSTORE_DIR, embedding_function=embeddings, client_settings=CHROMA_SETTINGS)
    retriever = vectorstore.as_retriever()

    prompt, memory = get_prompt_template(prompt_type=prompt_type)
    llm = load_llm(device, model_id=LLM_MODEL_ID, model_basename=LLM_MODEL_BASENAME, LOGGING=logging)

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        callbacks=callback_manager,
        chain_type_kwargs={
            "prompt": prompt,
        },
    )

    return qa_chain

def recognize_speech():
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
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    if sentiment > 0:
        return "Positive", sentiment
    elif sentiment < 0:
        return "Negative", sentiment
    else:
        return "Neutral", sentiment

def store_negative_sentiment(user_input, response, sentiment_score):
    with open("negative_sentiments.txt", "a") as file:
        file.write(f"User Input: {user_input}\n")
        file.write(f"Response: {response}\n")
        file.write(f"Sentiment Score: {sentiment_score}\n")
        file.write("---\n")

def execute_chat_chain(chain):
    while True:
        print("How would you like to communicate with the bot?")
        print("1. Type\n2. Speak")
        input_mode = input("Enter the number associated with your preferred method or type 'quit', 'q' or 'exit' to exit: ")
        if input_mode.lower() in ["quit", "q", "exit"]:
            break
        if input_mode.lower() not in ["1", "2"]:
            print("Invalid input mode. Please select 1 for 'chat' or 2 for 'voice'.")
            continue
        if input_mode == "1":
            user_input = input("> Question: ")
        elif input_mode == "2":
            user_input = recognize_speech()
            if user_input is None:
                continue
        sentiment, sentiment_score = analyze_sentiment(user_input)
        print(f"Sentiment: {sentiment} (Score: {sentiment_score:.2f})")
        start_time = time.time()
        response = chain.invoke({"input": user_input})
        response_time = time.time() - start_time
        print("\n> Answer:")
        print("\n" + response["answer"], end="\n\n")
        print(f"Response time: {response_time:.2f} seconds")
        if sentiment == "Negative":
            store_negative_sentiment(user_input, response["answer"], sentiment_score)

def main():
    """
    Main function to ingest documents, create a question-answering chain, and handle user queries.
    """
    ingest_documents()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    prompt_type = "llama"

    if not os.path.exists(MODELS_DIR):
        os.mkdir(MODELS_DIR)

    qa_chain = create_qa_chain(device, prompt_type=prompt_type)
    execute_chat_chain(qa_chain)

if __name__ == "__main__":
    logging.basicConfig(
        format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)s - %(message)s", level=logging.INFO
    )
    main()