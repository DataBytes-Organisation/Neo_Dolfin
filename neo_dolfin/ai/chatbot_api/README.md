# Dolfin Chatbot

This code implements a chatbot that can answer questions based on the content of a PDF file using the Llama-3-70b-8192 language model from Groq API and various natural language processing libraries.

## Development Specs
- Uses [Llama-3-70b-8192](https://console.groq.com/playground) language model from Groq and [Instructor Large](https://huggingface.co/hkunlp/instructor-large/tree/main) for embeddings.
- Developed using [Langchain](https://github.com/langchain-ai/langchain) 

## Getting Started
1. Navigate to the project directory:
   ```
   cd your-working-repository
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   ```

3. Activate the virtual environment:

   - For Windows:
     ```
     venv\Scripts\activate
     ```

   - For macOS and Linux:
     ```
     source venv/bin/activate
     ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up the Groq API key:
   - Go to the [Groq Console Playground](https://console.groq.com/playground) and create an account.
   - Generate an API key from the Groq Console.
   - Create a `.env` file in the project directory.
   - Add the following line to the `.env` file:
     ```
     GROQ_API_KEY=your_api_key
     ```
     Replace `your_api_key` with the API key obtained from the Groq Console.

## Usage

1. Prepare the knowledge base documents in the `KnowledgeBase` directory. Place the PDF file containing the relevant information for the chatbot.

2. Run the script:
   ```
   python llm_api.py
   ```

   The script will perform the following steps:
   - Ingest the documents from the `KnowledgeBase` directory.
   - Split the documents into chunks and store them in the vector store.
   - Load the embeddings model 
   - Create a question-answering chain using the loaded components.

3. Once the ingestion process is complete, you can enter your queries at the prompt. The script will use the question-answering chain to provide answers based on the ingested knowledge base.

4. To exit the script, type `quit` or `exit` at the prompt.

## Configuration

The script provides various configuration options that you can modify according to your requirements:

- `EMBEDDING_MODEL`: The embedding model used for document retrieval. It is set to `"hkunlp/instructor-large"` by default.
- `LLM_MODEL`: The language model used for generating responses. It is set to `"llama3-70b-8192"` by default. You can choose from other available models on Groq, such as `"llama-3-8b-8192"`, `"mixtral-8x7b-32768"`, or `"gemma-7b-it"`. The last numbers in the model name represent the maximum token size supported by the model.
- `LLM_TEMP`: The temperature setting for the language model. It is set to `0.1` by default.
- `CHUNK_SIZE`: The maximum chunk size for the embedding model. It is set to `8192` by default.
- `BASE_DIR`: The base directory of the project. It is automatically set to the directory containing the script.
- `DOCS_DIR`: The directory containing the knowledge base documents. It is set to `os.path.join(BASE_DIR, "KnowledgeBase")` by default.
- `VECTOR_STORE_PATH`: The directory where the vector store will be persisted. It is set to `os.path.join(BASE_DIR, "VectorStore")` by default.
- `MODEL_DIR`: The directory where the models will be stored. It is set to `os.path.join(BASE_DIR, "models")` by default.


## Potential Error Debug

- If you encounter an error related to a missing API key, make sure you have set up the `.env` file with your Groq API key as described in the "Getting Started" section.
