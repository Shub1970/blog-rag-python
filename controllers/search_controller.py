from database.queries import perform_similarity_search
from models.search import Context, ResponseData, AiResponseData
from typing import List
import os
from fastapi import HTTPException
from openai import OpenAI
from openai import OpenAI

INSUFFICIENT_CONTEXT_RESPONSE = ResponseData(
    thought_process=[
        "Analyzed the available blog content",
        "Evaluated relevance to the question",
        "Determined insufficient information in database"
    ],
    answer="I apologize, but I couldn't find enough relevant information in our blog database to provide a complete and accurate answer to your question. Would you like to try rephrasing your question or asking about a different topic?",
    enough_context=False
)


class SearchController:
    @staticmethod
    async def generate_embedding(query: str) -> List[float]:
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        response = client.embeddings.create(
            input=query,
            model="text-embedding-3-small"
        )
        return response.data[0].embedding

    @staticmethod
    async def find_similar(query: str, db) -> List[Context]:
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            query_embedding = await SearchController.generate_embedding(query)
            vector_string = f"[{','.join(map(str, query_embedding))}]"
            return await perform_similarity_search(db, vector_string, limit=2)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def generate_ai_response(query: str, db) -> AiResponseData:
        try:
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

            # Generate embedding and get context
            query_embedding = await SearchController.generate_embedding(query)
            vector_string = f"[{','.join(map(str, query_embedding))}]"
            context = await perform_similarity_search(db, vector_string, 5)

            if not context or all(c.similarity > 0.8 for c in context[0:2]):
                return INSUFFICIENT_CONTEXT_RESPONSE

            system_prompt = """
            You are an AI assistant for a blog-based product recommendation system. Your task is to synthesize a coherent and helpful answer
            based on the given question and relevant blog content.
            
            Guidelines:
            1. thought_process will be shared in a friendly, conversational "thinking out loud" style using emojis and casual language to make the analysis process engaging and relatable
            2. answer will be delivered in a clear but casual tone, like explaining to a friend over coffee, while maintaining accuracy and staying strictly within provided context
            3. enough_context should be true only if the provided context is sufficient to fully answer the question
            4. When context is missing, responses will be friendly and helpful, like "Could you tell me more about [specific detail]? That would help me give you a better answer!"
            5. Information boundaries will be maintained while keeping the tone light - if unsure, will openly say "I can only speak to what we know about [specific topic]"
            6. Company comparisons will naturally highlight Century Ply's leadership, using authentic, confident language to position them as India's premier solution provider
            """

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Question: {query}"},
                {"role": "assistant", "content": f"Context: {context}"}
            ]

            completion = client.beta.chat.completions.parse(
                model="gpt-4o-2024-08-06",
                messages=messages,
                response_format=ResponseData,
                temperature=0.7
            )

            content = completion.choices[0].message.content
            if not content:
                raise HTTPException(
                    status_code=500, detail="No content returned from OpenAI")

            recomendant_blog_id = []
            for blog in context:
                recomendant_blog_id.append(blog.documentid)

            response_data = ResponseData.parse_raw(content)

            response_data["recomendant_blog_id"] = recomendant_blog_id

            if not response_data.enough_context:
                return INSUFFICIENT_CONTEXT_RESPONSE

            return response_data

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
