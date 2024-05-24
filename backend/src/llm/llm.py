from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from openai import OpenAI


def llm_response(frames, historical) -> str:
    client = OpenAI()

    messages = [].extend(
        historical)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
    )
    print(response.choices[0].message.content)

    return response.choices[0].message.content
