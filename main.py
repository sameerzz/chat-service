from fastapi import FastAPI, HTTPException
from utils import get_book_details, add_book_func
app = FastAPI()
from pydantic import BaseModel
from chat_service import chat



class Book(BaseModel):
    id: int
    title: str
    author: str

class ChatRequest(BaseModel):
    message: str

@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = get_book_details(book_id)

    if book is None:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )

    return book


@app.post("/books")
def add_book(book: Book):
    existing_book = get_book_details(book.id)
    if existing_book is not None:
        raise HTTPException(
            status_code=400,
            detail="Book with this ID already exists"
        )
    
    added_book = add_book_func(book.model_dump())
    return added_book



@app.post("/chat")
def chat_endpoint(message:ChatRequest):
    response = chat(message.message)
    return {"response": response}

@app.get("/")
def home():
    return {
        "message": "Deployed automatically with Cloud Build!",
        "version": "2.0"
    }