# 1. PDF 불러와 문서 추출하기
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader

load_dotenv()
file_path = "/Users/techup/AIAGENT/datasets/한글맞춤법 표준어규정 해설.pdf"

loader = PyPDFLoader(file_path)
pages = loader.load()
# print("페이지 수 :", len(pages))
# print("첫 번째 페이지 정보:", pages[0])

# 2. 텍스트 분할하기
from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size = 500, chunk_overlap = 50)
docs = text_splitter.split_documents(pages)

# print(f"총 {len(docs)}개의 청크 생성 완료")
# print('각 청크의 길이', [len(i.page_content) for i in docs])

# for i in docs:
#     print("메타 데이터: ", i.metadata)
#     print("내용", i.page_content)
#     print("=" * 50)

# 벡터 스토어 생서하기
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

DB_PATH = "./chroma_db"

vectorstore = Chroma.from_documents(
    documents = docs,
    embedding = OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory=DB_PATH,
    collection_name="korean_pdf"
)

print(vectorstore.similarity_search("구개음화", k=3))

