from contextlib import asynccontextmanager
from fastapi import FastAPI
from dotenv import load_dotenv
from app.db import run_query, close_driver
from app.routers import onboarding, queries, memory
from app.memory import init_memory

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_memory() 
    yield
    close_driver()
    
app = FastAPI(title="CodeGraph", lifespan=lifespan)
app.include_router(onboarding.router)
app.include_router(queries.router)
app.include_router(memory.router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/db-check")
def db_check():
    rows = run_query("RETURN 1 AS value")
    return {"neo4j": "connected", "result": rows}