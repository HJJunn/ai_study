from typing import TypedDict, Annotated

def add(left, right):
    return left + right

class State(TypedDict):
    """
    메시지를 누적하여 저장하는 리듀서 함수를 지정하기 위해 Annotated 타입을 사용
    Annotated 타입은 메타데이터를 붙이는 기능을 제공하며, 리듀서 함수를 메타데이터로 등록하여 상태에 대한 추가 정보를 제공할 수 있습니다.
    """
    messages : Annotated[list[str], add]


# add_messages
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.message import add_messages

msg1 = [HumanMessage(content = "hello", id ="1")]
msg2 = [AIMessage(content="Hi there!", id = "2")]

print(add_messages(msg1, msg2))

# 동일한 아이디를 가지는 메시지 추가하기
msg3 = [HumanMessage(content = "heiil", id= "1")]
msg4 = [HumanMessage(content = "hello again", id = "1")]

print(add_messages(msg3, msg4))  

# 그래프의 상태에 리듀서 함수 사용하기
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import TypedDict, Annotated

class State(TypedDict):
    messages : Annotated[list[AnyMessage], add_messages]
    