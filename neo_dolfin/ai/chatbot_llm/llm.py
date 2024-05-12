import os
from langchain.document_loaders.csv_loader import CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import CTransformers
from langchain.chains import ConversationalRetrievalChain
from ctransformers import AutoConfig
from ctransformers import AutoModelForCausalLM

# Define paths for the vector store and temporary directory
DB_FAISS_PATH = "vectorstore/db_faiss"

def process_csv_file(file_path):
    print(f"Processing CSV file: {file_path}")
    
    # Load the CSV file using CSVLoader
    loader = CSVLoader(file_path=file_path, encoding="utf-8", csv_args={'delimiter': ','})
    data = loader.load()
    
    # Split the loaded data into text chunks using RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    text_chunks = text_splitter.split_documents(data)
    
    print(f"Total text chunks: {len(text_chunks)}")
    
    # Create embeddings using HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    
    # Create a FAISS vector store from the text chunks and embeddings
    docsearch = FAISS.from_documents(text_chunks, embeddings)
    
    # Save the vector store locally
    docsearch.save_local(DB_FAISS_PATH)
    
    return docsearch

def answer_question(query, qa):
    chat_history = []
    
    # Use the conversational retrieval chain to answer the query
    result = qa({"question": query, "chat_history": chat_history})
    
    return result['answer']

def main():
    print("Llama-2- Dolfin CSV Chatbot")
    
    csv_file_path = "data/transactions.csv"  # Replace with the actual path to CSV file 
    
    # Check if the CSV file exists
    if not os.path.isfile(csv_file_path):
        print("Invalid file path. Please provide a valid CSV file path.")
        return
    
    # Process the CSV file and create the vector store
    docsearch = process_csv_file(csv_file_path)
    
    # Initialize the language model (Llama-2)
    llm = CTransformers(model="models/llama-2-7b-chat.ggmlv3.q4_0.bin", model_type="llama", config={'max_new_tokens': 512, 'temperature': 1.0, 'context_length': 4000})
    
    # Create a conversational retrieval chain using the language model and vector store retriever
    qa = ConversationalRetrievalChain.from_llm(llm, retriever=docsearch.as_retriever())
    
    while True:
        print("\nEnter your query (type 'exit' to quit):")
        query = input("> ")
        
        if query.lower() == 'exit':
            break
        
        # Answer the user's query using the conversational retrieval chain
        response = answer_question(query, qa)
        print("Response:", response)

if __name__ == "__main__":
    main()