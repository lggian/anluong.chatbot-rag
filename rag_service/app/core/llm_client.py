import httpx

async def call_llm(prompt: str):
    async with httpx.AsyncClient() as client:
        res = await client.post(
            "http://localhost:8001/generate",
            params={"prompt": prompt}
        )
        return res.json()["response"]