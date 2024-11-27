from langchain_ollama import ChatOllama


def get_llm(model_name="mistral", temperature=0):
    return ChatOllama(model=model_name, temperature=temperature)
