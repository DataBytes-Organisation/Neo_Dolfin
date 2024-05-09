
# Llama-2 Dolfin CSV Chatbot (Not Fine-Tuned)

This code implements a chatbot that can answer questions based on the content of a CSV file using the Llama-2 language model and various natural language processing libraries.


## Development Specs
- Uses [Llama-2 7B](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/tree/main) and [Sentence Transformers](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) for robust functionality.
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

6. Download the Llama 2 Model:

Download the Llama 2 model file named `llama-2-7b-chat.ggmlv3.q4_0.bin` usning the following link:

[Download Llama 2 Model](https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML/tree/main)

### Model Information

| Name                           | Quant method | Bits | Size    | 
|--------------------------------|--------------|------|---------|
| llama-2-7b-chat.ggmlv3.q4_0.bin| q4_0         | 4    | 3.79 GB |

**Note:** After downloading the model, add the model file to the `models` directory. The file should be located at `models\llama-2-7b-chat.ggmlv3.q4_0.bin`, in order to run the code.

7. Run the chatbot:
   ```
   python llm.py
   ```