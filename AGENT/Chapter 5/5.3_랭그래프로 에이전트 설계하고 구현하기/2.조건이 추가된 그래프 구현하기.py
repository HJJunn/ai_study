# 그래프 상태 정의하기
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph
from langchain_openai import ChatOpenAI
from langgraph.graph import START,END
from dotenv import load_dotenv
from operator import add

# 1. 상태 정의 및 상태 그래프 생성
class State(TypedDict):
    messages : Annotated[list[str], add]
    question_length: int

graph_builder = StateGraph(State)

# 2. 질문의 길이를 저장하는 노드 만들기
def guardrail(state: State)->State:
    question_length = len(state["messages"][-1])

    return {
        "question_length" : question_length
    }
graph_builder.add_node("guardrail", guardrail)

load_dotenv()
llm = ChatOpenAI(model_name = "gpt-4o-mini")

def chatbot(state: State) -> State:
    question = state["messages"][-1]
    response = llm.invoke(question)
    return {
        "messages" : [response.content]
    }

graph_builder.add_node("chatbot", chatbot)

# 3. 라우팅 함수 정의하고 조건부 엣지 추가하기
def routing_function(state: State):
    if state["question_length"] > 3:
        return "chatbot"
    else:
        return END
    
graph_builder.add_conditional_edges(
    "guardrail",
    routing_function,
    {"chatbot" : "chatbot", END : END}
)

graph_builder.add_edge(START, "guardrail")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

# 에이전트 그래프 시각화 및 실행하기
from IPython.display import display, Image

try: 
    display(Image(graph.get_graph().draw_mermaid_png()))
except Exception:
    pass

print("길이가 3 이하인 경우:", graph.invoke({"messages" : ["hi"]})) # 바로 종료
print("길이가 3 초과인 경우:", graph.invoke({"messages" : ["hello"]})) # 챗봇 노드로 이동하여 답변 생성