import os
import shutil
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.graph_store import index_repo, is_git_url, clone_repo
from app.memory import log_run

router = APIRouter(prefix="/onboard", tags=["onboarding"])

class OnboardRequest(BaseModel):
    repo_path: str
    
@router.post("")
def onboard(req: OnboardRequest):
    if is_git_url(req.repo_path):
        local_path = clone_repo(req.repo_path)          # clone, get temp dir
        cleanup = True
    else:
        if not os.path.isdir(req.repo_path):
            raise HTTPException(status_code=400, detail=f"Path not found: {req.repo_path}")
        local_path = req.repo_path
        cleanup = False
    try:
        stats = index_repo(local_path)
        log_run("onboard", target=req.repo_path,
                result_count=stats["functions_indexed"],
                details=f"{stats['call_edges_indexed']} edges")
        return {"repo": req.repo_path, **stats}
    finally:
        if cleanup:
            shutil.rmtree(local_path, ignore_errors=True)