from typing import TypedDict
from pydantic import BaseModel

#TypeDict으로 데이터 타입에 맞는 값 만들기
class User(TypedDict):
    id : int
    name : str
    email : str

user1 : User = {
    "id" : 1,
    "name" : 123,  # TypeDict는 타입 검사를 하지 않기 때문에, name에 숫자를 넣어도 오류가 발생하지 않습니다.
    "email" : "example@example.com"
}
print("user1:", user1)

#pydantic으로 데이터 타입에 맞는 값 만들기
class User(BaseModel):
    id : int
    name : str
    email : str

user_data = {
    "id" : 1,
    "name" : "JUN",  # pydantic은 타입 검사를 하기 때문에, name에 숫자를 넣으면 오류가 발생합니다.
    "email" : "example@example.com"
}

user2 = User(**user_data)
print("user2:", user2)