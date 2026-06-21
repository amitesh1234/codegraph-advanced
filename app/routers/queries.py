from fastapi import APIRouter
from app.db import run_query
from app.memory import log_run
from app import services

router = APIRouter(prefix="/query", tags=["queries"])

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