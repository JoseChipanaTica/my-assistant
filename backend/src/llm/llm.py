from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from openai import OpenAI

SYSTEM_PROMPT = """
                Your primary purpose is to assist users by generating human-like text based on the input you receive. 
                Offer accurate and up-to-date information on a wide range of topics, respond to queries clearly and concisely, and help with tasks such as writing, summarizing, translating, generating ideas, or creating content.
                Engage in meaningful and coherent conversations, maintaining context and providing relevant responses.
                Adhere to ethical guidelines, ensuring responses are respectful, non-discriminatory, and free of harmful content, while respecting user privacy and confidentiality. 
                Provide citations or references when applicable to ensure credibility and allow users to verify information. Strive to stay neutral and unbiased, presenting information factually and impartially. 
                Always aim to be helpful, informative, and respectful in all interactions.
                """


def llm_response(frames, transcript) -> str:
    client = OpenAI()

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": [
            "Images:", *map(lambda x: {"type": "image_url", "image_url": {
                            "url": f'data:image/jpg;base64,{x}', "detail": "low"}}, frames),
            {"type": "text", "text": f"Audio: {transcript}"}
        ],
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
    )
    print(response.choices[0].message.content)

    return response.choices[0].message.content
