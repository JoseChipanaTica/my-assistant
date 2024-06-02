from typing import List

from langchain import hub
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.language_models import BaseChatModel


class Agent:
    def __init__(self, model: BaseChatModel) -> None:
        self.model = model
        self.executor = None

    async def start(self):
        search = TavilySearchResults()
        tools = [search]
        prompt = hub.pull("hwchase17/openai-tools-agent")

        agent = create_openai_functions_agent(
            self.model, tools, prompt
        )

        self.executor = AgentExecutor(agent=agent, tools=tools)

    async def ainvoke(self, text, messages: List):
        result = await self.executor.ainvoke({'input': text, 'chat_history': messages})
        return result
