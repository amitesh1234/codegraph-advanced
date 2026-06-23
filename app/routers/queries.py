from fastapi import APIRouter, HTTPException
from app.db import run_query
from app.memory import log_run
from app import services

router = APIRouter(prefix="/query", tags=["queries"])

@router.get("/search")
def search(query: str, limit: int = 10):
    rows = services.search_code(query, limit)
    log_run("search", target=query, result_count=len(rows))
    return {"query": query, "results": rows}


@router.get("/source")
def source(function_id: str):
    row = services.get_function_source(function_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Function not found")
    log_run("source", target=function_id, result_count=1)
    return row


@router.get("/who-calls")
def who_calls(name: str):
    rows = services.who_calls(name)
    log_run("who-calls", target=name, result_count=len(rows))
    return {"target": name, "callers": rows}


@router.get("/impact")
def impact(name: str, depth: int = 3):
    rows = services.impact_of_change(name, depth)
    log_run("impact", target=name, result_count=len(rows))
    return {"target": name, "depth": depth, "impacted_by_change": rows}


@router.get("/depends-on")
def depends_on(name: str, depth: int = 3):
    rows = services.depends_on(name, depth)
    log_run("depends-on", target=name, result_count=len(rows))
    return {"target": name, "depth": depth, "depends_on": rows}