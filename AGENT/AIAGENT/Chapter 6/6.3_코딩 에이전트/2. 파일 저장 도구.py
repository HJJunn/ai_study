from pydantic import Field
from langchain.tools import tool
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI


# 1. 파일을 저장하는 도구
@tool
def file_write_tool(
    file_path: str = Field(description="생성/수정할 파일의 경로"),
    content: str = Field(description="파일에 작성할 내용")
) -> str:
    """
    파일을 생성하거나 내용을 작성하는 도구입니다.
    
    Args:
        file_paht : 생성/수정할 파일의 경로
        content : 파일에 작성할 내용
        
    Returns:
        성공/실패 메시지
    
    """
    try: 
        with open(file_path, 'w', encoding = 'utf-8') as f:
            f.write(content)
        return f"파일 '{file_path}에 성공적으로 작성했습니다."
    except Exception as e:
        return f"파일 작성 실패 : {repr(e)}"
    
# 2. 두가지 도구 기반 에이전트 생성
from exec_tool import python_exec_tool

tools = [python_exec_tool, file_write_tool]

llm = ChatOpenAI(model = "gpt-4o")
graph = create_agent(llm, tools)

if __name__ == "__main__":
    response = graph.stream(
        {
            "messages" : [
                "첫번째 항이 1인 피보나치 수열을 출력하는 파이썬 코드를 작성해주세요. 정상적으로 실행되는지 확인도 해주세요.",
                "확인했다면 그 코드는 .py 파일로 저장하세요."
            ]
        }
    )
    for chunk in response:
        for node, value in chunk.items():
            if node:
                print("---", node, "---")
            if "messages" in value:
                print(value["messages"][0].content)
    