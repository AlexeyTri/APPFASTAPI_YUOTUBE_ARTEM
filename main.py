from fastapi import FastAPI, Request, status
from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import ValidationError
from fastapi.responses import JSONResponse

fake_users = [
    {"id": 1, "role": "admin", "name": "Bob"},
    {"id": 2, "role": "investor", "name": "John"},
    {"id": 3, "role": "trader", "name": "Matt"},
    {"id": 4, "role": "investor", "name": "Homer", "degree": [
        {"id": 1, "created_at": "2020-01-01T00:00:00", "type_degree": "expert"}
    ]},
]

fake_trades = [
    {"id": 1,"user_id": 1, "currency": "BTC", "side": "buy", "price": 123, "amount": 2.12},
    {"id": 2,"user_id": 1, "currency": "BTC", "side": "buy", "price": 123, "amount": 2.12}
]

fake_users2 = [
    {"id": 1, "role":"admin", "name": "Bob"},
    {"id": 2, "role":"investor", "name": "John"},
    {"id": 3, "role":"traider", "name": "Matt"},
]

# BaseModel - класс pydentic
class Trade(BaseModel):
    id: int
    user_id: int
    currency: str = Field(max_length=5)
    side: str
    price: float = Field(ge=0)
    amount: float

class DegreeType(Enum):
    newbie = "newbie"
    expert = "expert"

class Degree(BaseModel):
    id: int
    created_at: datetime
    type_degree: DegreeType

class User(BaseModel):
    id: int
    role: str
    name: str
    degree: Optional[List[Degree]] = []
    # degree: List[Degree]


app = FastAPI(title="DOG_APP")


# запрос на получение конкретного пользователя по id
@app.get('/user/{user_id}', response_model=List[User])
async def get_user(user_id: int):
    return [user for user in fake_users if user.get('id') == user_id]

# передаем параметры внутрь запроса, в данном примере хотим получить данные по конкретной сделке
@app.get('/trades')
async def get_traides(limit: int = 1, offset: int = 0):
    return fake_trades[offset:][:limit]

# комбинируем параметры пути и параметры запроса
@app.post('/users/{user_id}')
async def change_user_name(user_id: int, new_name: str):
    current_user = list(filter(lambda user: user.get('id') == user_id, fake_users2))[0]
    current_user['name'] = new_name
    return {'status': 200, 'data': current_user}

# пример валидации данных. Добаыляем новую операцию в базу данных операций
@app.post('/traides')
async def add_traides(trades: List[Trade]):
    fake_trades.extend(trades)
    return {'status': 200, 'data': fake_trades}

@app.exception_handler(ValidationError)
async def validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({'detail': exc.errors()})
    )