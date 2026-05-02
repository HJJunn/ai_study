from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph

class State(TypedDict):
    messages: Annotated[list[str], add]

graph = StateGraph(State)

def chatbot(state : State):
    question = state["messages"]
    answer = f"사용자: {question}"
    return {"messages":[answer]}

graph.add_node("chatbot", chatbot)

# 시작점과 종료점 엣지 연결하기
from langgraph.graph import START, END
graph.add_edge(START, "chatbot")
graph.add_edge("chatbot", END)

# 노드 사이에 엣지 추가하기
# graph.add_edge("node_a", "node_b")

# 라우팅 함수 정의하고 조건부 엣지 추가하기
def routing_function(state: State):
    if len(state["messages"][-1].content) > 1000:
        return True
    return False

graph.add_conditional_edges("chatbot", routing_function, {True : "summary", False : END})
