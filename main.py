from fastapi import FastAPI
from routers import search_router
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

app.include_router(search_router.router)
