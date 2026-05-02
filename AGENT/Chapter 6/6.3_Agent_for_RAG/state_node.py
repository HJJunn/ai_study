from langgraph.graph import MessagesState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import ToolMessage, AIMessage
from retriever import retriever, retriever_tool

# 상태 정의
class AgentState(MessagesState):
    question : str
    context : str
    answer : str
    retry_num : int

# 검색 도구 호출하는 LLM 노드
llm = ChatOpenAI(model = 'gpt-4o')

def chatbot(state: AgentState):
    print("----[Chatbot]-----")
    messages = state["messages"]
    llm_with_tools = llm.bind_tools([retriever_tool])
    response = llm_with_tools.invoke(messages)

    return {
        "messages" : [response],
        "question" : messages[-1].content,
    }

# 관련 문서 검색 노드
def retrieve(state: AgentState):
    print("----[Retriever]-----")
    question = state["question"]
    relevant_doc = retriever.invoke(question)
    context = ""
    for doc in relevant_doc:
        context += f"Page {doc.metadata["page"] + 1} : {doc.page_content}\n"

    # Tool 호출에 대한 응답 메시지 생성
    last_message = state["messages"][-1]

    if hasattr(last_message, "tool_calls") and len(last_message.tool_calls) > 0:
        tool_call_id = last_message.tool_calls[0]["id"]
        tool_message = ToolMessage(
            content = context,
            name = "retriever",
            tool_call_id = tool_call_id
        )
        return {"messages": [tool_message], "context" : context}
    else:
        return {"messages" : [context], "context" : context}
    
# 검색 결과 정리하는 노드
def context_organizer(state: AgentState):
    print("----[Context Organizer]-----")
    context = state["context"]

    context_organizer_prompt = ChatPromptTemplate.from_messages(
        [
            ("system",
             """당신은 검색 증강 생성을 위한 검색 문서를 정리하는 전문가입니다.
             다음은 검색된 결과 문서를 확인하고, LLM이 해당 문서를 정리된 형태로 참고할 수 있습니다.
             
             문서의 불필요한 공백 등을 삭제하거나 정렬을 다시하여 정리된 형태로 반환해주세요.
             내용을 삭제하는 것을 최소로 합니다. 페이지 번호 정보를 절대 삭제하지 마세요."""
             ),
             (
                 "user",
                 """
                 검색 결과 : {context}
                 """
             ),
        ]
    )
    context_organizer = context_organizer_prompt | llm
    orgainzed_context = context_organizer.invoke({"context" : context})

    return {
        "context": orgainzed_context.content, 
        "messages": [AIMessage(orgainzed_context.content)]
        }

# 쿼리 재작성 노드
def transform_query(state: AgentState):
    """
    더 나은 질문을 생성하기 위해 쿼리를 반환

    Args: 
        state (dict): 현재 그래프 상태
    Returns:
        state (dict): 재구성된 질문으로 question 키를 업데이트
    """
    print("----[TRANSFORM QUERY]------")
    question = state['question']

    system = """
    당신은 질문을 다시 작성하는 전문가입니다. 입력된 질문은 벡터 저장소 검색에 최적화된 더 나은 버전으로 변환하세요.
    입력을 살펴보고 질문의 핵심적읜 의미와 의도를 파악하여 개선된 질문을 만들어주세요.
    """
    rewrite_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system", system
            ),
            (
                "user",
                "다음은 초기 질문입니다. : \n\n {question}\n 한국어로 개선된 질문을 작성해주세요."
            )
        ]
    )
    question_rewriter = rewrite_prompt | llm
    better_question = question_rewriter.invoke({"question" : question})

    return {
        "question" : better_question.content,
        "messages": [better_question],
        "retry_num": state["retry_num"] + 1 if state.get("retry_num") else 1
    }

# 최종 답변 노드
def generate(state: AgentState):
    print("----[GENERATE]-----")
    question = state["question"]
    context = state["context"]

    retry_num = state.get("retry_num", 0)

    if retry_num >=3:
        rag_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
                    당신은 검색된 문서를 통해 해결하는 수 있는 질무을 추출하는 어시스턴트입니다.
                    사용자가 해결하고자 한 질문이 있었으나 검색 컨텍스트가 충분하지 않는 상황이므로,
                    주어진 검색 결과 내에서 답변할 수 있는 질문을 새롭게 작성해 나열하세요.
                    사용자에게 질문에 대한 답변을 하지 못함에 양해를 구하고, 다른 질문의 기회와 선택지를 제공하는 친절한 가이드를 하세요.
                    """
                ),
                (
                    "user",
                    "질문 : {question} \n\n 검색결과; {context} \n\n 답변"
                )
            ]
        )
    else:
        rag_prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system"
                )
            ]
        )