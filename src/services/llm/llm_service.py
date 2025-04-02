from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

#if extra models are added we need to refactor the function below and constants above
DEFAULT_MODEL = "gpt-4o-mini" 

def get_openai_model():
    llm = ChatOpenAI(model=DEFAULT_MODEL, openai_api_key=OPENAI_API_KEY)
    return llm

def get_chain(prompt):
    llm = get_openai_model()
    chain = prompt | llm
    return chain
  

  