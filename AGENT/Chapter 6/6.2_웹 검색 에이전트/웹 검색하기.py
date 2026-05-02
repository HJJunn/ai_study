from langchain_tavily import TavilySearch
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

tool = TavilySearch(max_results =2)
tools = [tool]

llm = ChatOpenAI(model = 'gpt-4o')
llm_with_tools = llm.bind_tools(tools)

response = llm_with_tools.invoke("2026년 AI 트렌드는 무엇인가요?")
print(response)
print(response.tool_calls)