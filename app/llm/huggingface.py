import os
from dotenv import load_dotenv
load_dotenv()
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace


HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")
if not HUGGINGFACE_TOKEN:
    raise ValueError("HUGGINGFACE_TOKEN is not set")

llm = HuggingFaceEndpoint(
    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
    max_new_tokens=512,
    huggingfacehub_api_token=HUGGINGFACE_TOKEN
)

chat_model = ChatHuggingFace(llm=llm)



if __name__ == "__main__":
    response = chat_model.invoke("What is the capital of France?")
    print(response)