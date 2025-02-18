from fastapi import APIRouter, Depends
import asyncpg
from models.search import Query, SearchResponse, ResponseData
from controllers.search_controller import SearchController
from database.connection import get_db

router = APIRouter()

@router.post("/blog/similar", response_model=SearchResponse)
async def find_similar(
    query_data: Query,
    db: asyncpg.Connection = Depends(get_db)
):
    context = await SearchController.find_similar(query_data.query, db)
    return SearchResponse(
        message="Similar blogs found",
        results=context
    )

@router.post("/blog/ai-response", response_model=ResponseData)
async def generate_ai_response(
    query_data: Query,
    db: asyncpg.Connection = Depends(get_db)
):
    return await SearchController.generate_ai_response(query_data.query, db)