import httpx
import asyncio

async def test_search():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:52059/blog/similar",
            json={"query": "veener, club-prime, laminate"}
        )
        print("Status Code:", response.status_code)
        print("Response JSON:", response.json())

if __name__ == "__main__":
    asyncio.run(test_search())
