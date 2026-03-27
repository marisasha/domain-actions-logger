from fastapi import FastAPI
from src.router import main_router

app = FastAPI()
app.include_router(main_router)

{
    "username": "marisasha",
    "password": "123",
    "first_name": "Александр",
    "last_name": "Маринушкин",
    "email": "marisasha228@bk.ru",
    "birth_date": "2006-11-27T00:00:00",
    "phone": "+79296785354",
}
