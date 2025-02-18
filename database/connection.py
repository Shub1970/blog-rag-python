# app/database/connection.py
import os
import asyncpg
from fastapi import HTTPException
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    try:
        conn = await asyncpg.connect("postgresql://neondb_owner:npg_g3hSUYKx2Nob@ep-autumn-forest-a81fpt90-pooler.eastus2.azure.neon.tech/century-ply-database-ai?sslmode=require")
        logger.info("Database connection established")
        yield conn
    except asyncpg.PostgresError as e:
        logger.error(f"Database connection error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Could not connect to database"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    finally:
        if 'conn' in locals():
            await conn.close()
            logger.info("Database connection closed")