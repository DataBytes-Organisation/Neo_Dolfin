# Llama.cpp Dolfin Chatbot

This code implements a chatbot that can answer questions based on the content of a pdf file using the Llama.cpp (which uses Llama 2) language model and various natural language processing libraries.


## Development Specs
- Uses [Llama-2 7B](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/tree/main) incorporation with [Llama.cpp](https://github.com/ggerganov/llama.cpp) and [Sentence Transformers](https://huggingface.co/hkunlp/instructor-large/tree/main) for robust functionality.
- Developed using [Langchain](https://github.com/langchain-ai/langchain) 


## Getting Started
1. Navigate to the project directory:
   cd your-working-repository

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

5. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Prepare the knowledge base documents in the `KnowledgeBase` directory as here we have used the DOLFIN FAQs.pdf file as personal knowledge base for the chatbot.

2. Run the script:

   ```
   python llama_cpp.py
   ```

   The script will perform the following steps:
   - Ingest the documents from the `KnowledgeBase` directory.
   - Split the documents into chunks and store them in the vector store.
   - Load the embeddings model and language model (Model will be autometically downloaded in the provided `./models` path make sure you have enough space on the disk ≈5-6GBs).
   - Create a question-answering chain using the loaded components.

3. Once the ingestion process is complete, you can enter your queries at the prompt. The script will use the question-answering chain to provide answers based on the ingested knowledge base.

4. To exit the script, type `exit` at the prompt.

## Configuration

The script provides various configuration options that you can modify according to your requirements:

- `ROOT_DIR`: The root directory of the project. It is automatically set to the directory containing the script.
- `DOCUMENTS_DIR`: The directory containing the knowledge base documents. It is set to `f"{ROOT_DIR}/KnowledgeBase"` by default.
- `NUM_INGEST_THREADS`: The number of threads to use for document ingestion. It is set to the number of available CPU cores or 8 by default.
- `CHUNK_SIZE`: The size of the document chunks in characters. It is set to 4096 by default.
- `MAX_CHUNK_OVERLAP`: The maximum overlap between document chunks in characters. It is set to 200 by default.
- `MAX_TOKENS`: The maximum number of tokens allowed in a chunk. It is set to the same value as `CHUNK_SIZE` by default.
- `NUM_GPU_LAYERS`: The number of GPU layers to use for the language model. It is set to 100 by default.
- `BATCH_SIZE`: The batch size for the language model. It is set to 512 by default.
- `CHROMA_SETTINGS`: The settings for the Chroma database. It includes options for anonymized telemetry and persistence.
- `DOC_LOADER_MAP`: A mapping of file extensions to their corresponding document loaders. It allows the script to use the appropriate loader based on the file type.
- `EMBEDDINGS_MODEL_NAME`: The name of the embeddings model to use. It is set to `"hkunlp/instructor-large"` by default.
- `LLM_MODEL_ID`: The ID of the language model to use. It is set to `"TheBloke/Llama-2-7b-Chat-GGUF"` by default.
- `LLM_MODEL_BASENAME`: The base name of the language model file. It is set to `"llama-2-7b-chat.Q4_K_M.gguf"` by default.


## Potential error debug
- C++ Compiler
If you encounter an error while building a wheel during the pip install process, you may need to install a C++ compiler on your computer.

- For Windows 10/11

1. Install Visual Studio 2022.
2. Make sure the following components are selected:
   * Universal Windows Platform development
   * C++ CMake tools for Windows