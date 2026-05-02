from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from dotenv import load_dotenv

load_dotenv()
# 1. 타빌리 서치 도구 및 LLM 설정하기
tool = TavilySearch(max_results = 3)
tools = [tool]

llm = ChatOpenAI(model = 'gpt-4o')
llm_with_tools = llm.bind_tools(tools)

# 2. 상태 그래프 생성하기
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# 3. 노드 생성하기: LLM 노드
def chatbot(state: State):
    response = llm_with_tools.invoke(state["messages"])
    return {"messages" : [response]}

graph_builder.add_node("chatbot", chatbot)

# 4. 노드 생성하기: 도구 노드
import json
from langchain.messages import ToolMessage

class BasicToolNode:
    """마지막 AIMessage에서 요청된 도구를 실행하는 노드"""
    def __init__(self, tools: list) -> None:
        self.tools_by_name = {tool.name : tool for tool in tools}
    def __call__(self, inputs: dict):
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("입력된 메시지가 없습니다.")
        
        outputs = []
        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(tool_call["args"])
            outputs.append(
                ToolMessage(
                    content = json.dumps(tool_result, ensure_ascii=False),
                    name = tool_call["name"],
                    tool_call_id = tool_call["id"]
                )
            )
        return {"messages" : outputs}

tool_node = BasicToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# 5. 엣지 생성하기
def route_tools(
        state: State
):
    """마지막 메시지에 도구 호출이 있는 경우, ToolNode로 라우팅 그렇지 않으면 END로 라우팅"""
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"Error: 입력에 메시지가 없습니다. 상태: {state}")
    
    # tool_calls 속성이 존재하는지, tool_calls 속성이 비어있지 않은지 여부
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) >0: 
        return "tools"
    return END

graph_builder.add_conditional_edges(
    "chatbot", route_tools, {"tools" : "tools", END: END}
)

# 6. 엣지 생성 및 그래프 컴파일
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")
graph = graph_builder.compile()

# 7. 그래프 시각화하여 저장하고 실행하기
# if __name__ == "__main__":
#     try: 
#         image = graph.get_graph().draw_mermaid_png()
#         with open("web_agent/graph.png", "wb") as f:
#             f.write(image)
#     except Exception:
#         pass

#     response = graph.invoke(
#         {
#             "messages" : ["LangGraph가 무엇인가요?"]
#         }
#     )
#     print(response)

# pretty_print()를 사용해 메시지 목록 출력하기
# def invoke():
#     """메시지를 구분자와 함께 읽기 쉬운 형태로 출력"""
#     response = graph.invoke(
#         {"messages": ["Langraph가 무엇인가요?"]}
#     )
#     for msg in response["messages"]:
#         msg.pretty_print()

# if __name__ == "__main__":
#     invoke()


# # ainvoke() 사용
# async def ainvoke():
#     """비동기 방식으로 여러 요청을 동시에 처리 가능"""
#     response = await graph.ivoke(
#         {
#             "messages" : ["LangGraph가 무엇인가요?"]
#         }
#     )

#     for msg in response["messages"]:
#         msg.pretty_print()

# if __name__ == "__main__":
#     import asyncio
#     asyncio.run(ainvoke())

# stream : updates 모드 사용하기
# def stream():
#     """각 노드의 상태 업데이트만 출력돼는 방식"""
#     response = graph.stream(
#         {
#             "messages" : ["LangGraph가 무엇인가요?"]
#         }
#     )
#     for chunk in response:
#         for node, state in chunk.items():
#             # print("---", node, "---")
#             # print(state)
#             # print("=" * 60)
#             print(state["messages"][-1].pretty_print())
            

# if __name__ == "__main__":
#     stream()

# # stream()의 values 모드
# def stream_values():
#     """각 노드 단계에서의 현재 상태값을 출력"""
#     response = graph.stream(
#         {"messages" : ["LangGraph가 무엇인가요?"]},
#         stream_mode = "values"
#     )

#     for chunk in response:
#         for state_key, state_value in chunk.items():
#             print("---현재 상태---")
#             for msg in state_value:
#                 print(f"{type(msg).__name__}: {msg.content[:50]}")
#             if state_key == "messages":
#                 state_value[-1].pretty_print()
#             print("=" * 60)

# if __name__ == "__main__":
#     stream_values()

# # stream의 messages 모드
# def stream_messages():
#     """각 단계의 메시지 상태만 출력"""
#     response = graph.stream(
#         {"messages" : ["LangGraph가 무엇인가요?"]},
#         stream_mode = "messages"
#     )
#     for token, metadata in response:
#         print(token.content)

# if __name__ == "__main__":
#     stream_messages()

# astream()을 활용해 실행 결과 확인
async def astream():
    """모든 스트리밍 방식 비동기 방식으로 처리"""
    response = graph.astream(
        {"messages" : ["Langraph가 무엇인가요?"]}
    )
    async for chunk in response:
        for node, state in chunk.items():
            print("---", node, "---")
            print(state)
            print("=" * 60)
if __name__ == "__main__":
    import asyncio
    asyncio.run(astream())
    