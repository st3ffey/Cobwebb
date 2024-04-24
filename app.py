import gradio as gr
from src.pipeline import *

def main():
    interface = gr.Interface(
        fn=get_chat_response,
        inputs=[
            gr.Textbox(label="Question:"),
            gr.Number(label="Number of documents to initially retrieve:", value=25, precision=0),
            gr.Number(label="Number of documents to rerank and return:", value=8, precision=0)
        ],
        outputs=[
            gr.Textbox(label="Answer:"),
            gr.Textbox(label="The answer was pulled from the following proxy (url included) and chunks of text:")
        ],
        title="Chat with 2023 Proxy Filings!",
        description="Enter your question about a proxy, and receive a response from the chatbot using reranked retrieval."
    )
    interface.launch(debug=True)

if __name__ == "__main__":
    main()
