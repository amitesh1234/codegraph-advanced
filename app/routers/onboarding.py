import os
import shutil
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph_store import index_repo, is_git_url, clone_repo, parse_local_path
from app.memory import log_run

router = APIRouter(prefix="/onboard", tags=["onboarding"])

class OnboardRequest(BaseModel):
    repo_path: str
    
@router.post("")
def onboard(req: OnboardRequest):
    local_path, cleanup = parse_local_path(req.repo_path)
    try:
        stats = index_repo(local_path)
        log_run("onboard", target=req.repo_path,
                result_count=stats["functions_indexed"],
                details=f"{stats['call_edges_indexed']} edges")
        return {"repo": req.repo_path, **stats}
    finally:
        if cleanup:
            shutil.rmtree(local_path, ignore_errors=True)