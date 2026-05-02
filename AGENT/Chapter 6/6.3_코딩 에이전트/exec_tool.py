from pydantic import Field
from langchain.tools import tool

# 1. 코드 실행하는 도구 생성하기
@tool 
def python_exec_tool(
    imports: str = Field(description="임포트 구문"),
    code: str = Field(description="임포트 구문을 제외한 코드 블록")
) -> str:
    """
    파이썬 코드를 실행하는 도구입니다. 만약 코드에 실패한다면 에러 메시지를 반환합니다.
    실행 결과를 확인하고 싶다면 print(...)를 사용하여 출력해야 합니다.
    
    Args:
        imports: 임포트 구문
        code: 임포트 구문을 제외한 코드 블록
    
    Returns:
        실행 결과 또는 에러 메시지
    """

    # Check imorts
    try:
        exec(imports)
    except Exception as e:
        return f"모듈을 임포트하는데 실패했습니다. {repr(e)}"
    
    # Check execution
    try: 
        exec(imports + "\n" + code)
    except Exception as e:
        return f"코드 실행에 실패했습니다. {repr(e)}"
    
    result_str = f"성공적으로 코드가 실행되었습니다. :\n ```python\n{code}\n```"

    return result_str

# 2. create_agent 기반 에이전트 구축하기
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

load_dotenv()
tools = [python_exec_tool]
llm = ChatOpenAI(model = "gpt-4o")
graph = create_agent(llm, tools)

# 3. 에이전트 답변 확인하기
if __name__ == "__main__":
    response = graph.stream(
        {
            "messages" : [
                "첫번째 항이 1인 피보나치 수열을 출력하는 파이썬 코드를 작성해주세요."
            ]
        }
    )
    for chunk in response:
        for node, value in chunk.items():
            if node:
                print("---", node, "---")
            if "messages" in value:
                print(value["messages"][0].content)