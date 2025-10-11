"""Pipeline router for running recruitment pipelines."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend_api.auth import get_current_user
from src.backend_api.database import get_db
from src.backend_api.models import User, Project, ProjectStatus
from src.backend_api.schemas import PipelineRunRequest, PipelineRunResponse, PipelineStatusResponse
from src.backend_api.pipeline import PipelineOrchestrator, PipelineException

router = APIRouter(prefix="/pipeline", tags=["pipeline"])


@router.post("/run", response_model=PipelineRunResponse)
async def run_pipeline(
    request: PipelineRunRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PipelineRunResponse:
    """Run recruitment pipeline on job description.

    Args:
        request: Pipeline run request with job description
        current_user: Authenticated user
        db: Database session

    Returns:
        Pipeline execution results

    Raises:
        HTTPException: 400 if pipeline execution fails
    """
    # Create project record (status=running)
    project = Project(
        user_id=current_user.user_id,
        job_description_text=request.job_description_text,
        status=ProjectStatus.RUNNING,
    )

    db.add(project)
    await db.commit()
    await db.refresh(project)

    try:
        # Execute pipeline
        orchestrator = PipelineOrchestrator()
        result = await orchestrator.execute_pipeline(request.job_description_text)

        # Update project with results
        from datetime import datetime
        project.status = ProjectStatus.COMPLETED
        project.pipeline_start_time = orchestrator.start_time
        # Parse end_time string to datetime if it's a string
        end_time = result["metadata"]["end_time"]
        if isinstance(end_time, str):
            project.pipeline_end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
        else:
            project.pipeline_end_time = end_time
        project.candidate_count = result["metadata"]["candidates_found"]
        project.results_json = result

        await db.commit()

        return PipelineRunResponse(
            project_id=project.project_id,
            status="success",
            candidates=result["candidates"],
            ranked_candidates=result["ranked_candidates"],
            outreach_messages=result["outreach_messages"],
            metadata=result["metadata"],
        )

    except PipelineException as e:
        # Update project status to failed
        project.status = ProjectStatus.FAILED
        project.results_json = {
            "error": str(e),
            "module": e.module_name,
        }
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pipeline execution failed: {str(e)}",
        )

    except Exception as e:
        # Update project status to failed
        project.status = ProjectStatus.FAILED
        project.results_json = {"error": str(e)}
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/status/{project_id}", response_model=PipelineStatusResponse)
async def get_pipeline_status(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PipelineStatusResponse:
    """Get pipeline execution status.

    Args:
        project_id: Project ID to check status
        current_user: Authenticated user
        db: Database session

    Returns:
        Pipeline status information

    Raises:
        HTTPException: 404 if project not found, 403 if unauthorized
    """
    # Fetch project
    result = await db.execute(
        select(Project).where(Project.project_id == project_id)
    )
    project = result.scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Verify user owns project
    if project.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this project",
        )

    # Determine progress percentage
    progress_percentage = 0
    if project.status == ProjectStatus.COMPLETED:
        progress_percentage = 100
    elif project.status == ProjectStatus.FAILED:
        # Use last known progress from results_json if available
        if project.results_json and "metadata" in project.results_json:
            progress_percentage = project.results_json["metadata"].get("progress", 0)
    elif project.status == ProjectStatus.RUNNING:
        # For running projects, we can't track real-time progress yet
        # In a real implementation, this would come from a background task
        progress_percentage = 50

    # Extract current module if available
    current_module = None
    if project.results_json and "metadata" in project.results_json:
        module_results = project.results_json["metadata"].get("module_results", {})
        # Find the last completed module
        if module_results:
            completed_modules = [k for k, v in module_results.items() if v.get("status") == "success"]
            if completed_modules:
                last_module = max(completed_modules)
                current_module = f"Completed {last_module}"

    return PipelineStatusResponse(
        project_id=project.project_id,
        status=project.status.value,
        current_module=current_module,
        progress_percentage=progress_percentage,
        started_at=project.pipeline_start_time,
        completed_at=project.pipeline_end_time,
    )
