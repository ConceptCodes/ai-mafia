from pydantic.v1 import BaseModel, Field
from langchain_ollama import ChatOllama


class Jokes(BaseModel):
    """List of jokes to tell user."""

    jokes: str = Field(
        description="List of jokes to tell the user, separated by a semicolon"
    )


structured_llm = ChatOllama(model="mistral", temperature=0).with_structured_output(schema=Jokes)

# respone = structured_llm.invoke(
#     "You MUST tell me more than one joke about cats, and split them with a semicolon"
# )

raw_response = structured_llm.invoke(
    "You MUST tell me more than one joke about cats, separated by semicolons, in JSON format like {'jokes': 'joke1; joke2; ...'}"
)

print(raw_response)
