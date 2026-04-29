# 그래프의 입력 스키마와 출력 스키마 정의하기
from typing import TypedDict, Annotated
from operator import add

class InputState(TypedDict):
    question : str

class OutputState(TypedDict):
    answer : str

class OverallState(TypedDict):
    messages : Annotated[list[str], add]
    question : str
    answer : str

# 그래프 객체 생성하기
from langgraph.graph import StateGraph

graph_builder = StateGraph(
    state_schema=OverallState,
    input_schema=InputState,
    output_schema=OutputState
)

# LLM의 답변을 생성하는 노드 추가하기
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()
llm = ChatOpenAI(model_name = "gpt-4o-mini")

def chatbot(state: InputState) -> OutputState:
    question = state["question"]
    response = llm.invoke(question)
    return {
        "answer": response.content,
        "messages": [question, response.content]
    }

graph_builder.add_node("chatbot", chatbot)

# 챗봇 노드에 엣지를 연결하고 그래프 컴파일하기
from langgraph.graph import START, END
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

# 그래프 시각화하기
from IPython.display import display, Image
try:
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    pass

print(graph.invoke({"question" : "대한민국의 수도는 어디인가요?"}))

