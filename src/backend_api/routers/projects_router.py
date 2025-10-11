"""Projects router for managing recruitment projects."""

import logging
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend_api.auth import get_current_user
from src.backend_api.database import get_db

logger = logging.getLogger(__name__)
from src.backend_api.models import User, Project, ProjectStatus, ShortlistedCandidate, OutreachMessage, FollowUpSequence
from src.backend_api.schemas import (
    ProjectListResponse,
    ProjectSummary,
    ProjectDetailResponse,
    QuickStartParseRequest,
    QuickStartParseResponse,
    CreateProjectRequest,
    SourceCandidatesResponse,
    RankCandidatesResponse,
    ShortlistCandidatesRequest,
    ShortlistCandidatesResponse,
    ShortlistedCandidateResponse,
    ToggleShortlistResponse,
    EnrichCandidateResponse,
    GenerateOutreachResponse,
    OutreachMessageResponse,
    UpdateOutreachRequest,
    RegenerateOutreachResponse,
    GenerateFollowUpsResponse,
    FollowUpSequenceResponse,
)

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/quick-start/parse", response_model=QuickStartParseResponse)
async def parse_quick_start(
    request: QuickStartParseRequest,
    current_user: User = Depends(get_current_user),
) -> QuickStartParseResponse:
    """Parse natural language quick-start text into structured project fields.

    Args:
        request: Quick-start text description
        current_user: Authenticated user

    Returns:
        Extracted project fields

    Examples:
        Input: "Senior Python developers in Chennai with Django and FastAPI for Q1 2025"
        Output: {
            project_name: "Q1 2025 Hiring",
            job_title: "Senior Python Developer",
            location: "Chennai",
            skills: ["Django", "FastAPI", "Python"],
            ...
        }
    """
    try:
        from src.jd_parser.parser import JDParser
        from datetime import datetime

        logger.info(f"Parsing quick-start text: {request.quick_text[:100]}...")

        # Use JD Parser to extract structured data
        jd_parser = JDParser()

        # Create a minimal JD from the quick text to leverage the parser
        minimal_jd = f"""
Role: As described below
Location: As described below
Description: {request.quick_text}

We are looking for: {request.quick_text}
        """.strip()

        job_req = jd_parser.parse(minimal_jd)

        # Extract fields
        job_title = job_req.role or "Software Developer"
        location = job_req.location_preferences[0] if job_req.location_preferences else None
        skills = (job_req.required_skills or []) + (job_req.preferred_skills or [])

        # Generate project name from current quarter/year
        current_month = datetime.now().month
        quarter = f"Q{(current_month - 1) // 3 + 1}"
        year = datetime.now().year
        project_name = f"{quarter} {year} {job_title} Hiring"

        # Format experience years
        experience_years = None
        if job_req.years_of_experience and job_req.years_of_experience.min:
            min_years = job_req.years_of_experience.min
            max_years = job_req.years_of_experience.max if job_req.years_of_experience.max else None
            if max_years:
                experience_years = f"{min_years}-{max_years} years"
            else:
                experience_years = f"{min_years}+ years"

        # Generate full JD text
        jd_text = f"""Role: {job_title}

{request.quick_text}

Required Skills: {', '.join(skills[:5]) if skills else 'To be determined'}
Location: {location or 'Remote/Global'}
Experience: {experience_years or 'To be determined'}
        """.strip()

        logger.info(f"Extracted: title={job_title}, location={location}, skills={skills[:3]}")

        return QuickStartParseResponse(
            project_name=project_name,
            job_title=job_title,
            location=location,
            skills=skills[:10],  # Limit to top 10
            experience_years=experience_years,
            job_description_text=jd_text,
        )

    except Exception as e:
        logger.error(f"Failed to parse quick-start text: {e}")
        import traceback
        logger.error(traceback.format_exc())

        # Fallback: return basic extraction
        return QuickStartParseResponse(
            project_name=f"New Hiring Project {datetime.now().strftime('%Y-%m-%d')}",
            job_title="Software Developer",
            location=None,
            skills=[],
            experience_years=None,
            job_description_text=request.quick_text,
        )


@router.post("", response_model=ProjectDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    request: CreateProjectRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectDetailResponse:
    """Create a new project.

    Args:
        request: Project creation request with name, job_title, and job_description_text
        current_user: Authenticated user
        db: Database session

    Returns:
        Created project details with status=draft

    Raises:
        HTTPException: 400 if validation fails
    """
    # Create new project
    new_project = Project(
        user_id=current_user.user_id,
        name=request.name,
        job_title=request.job_title,
        job_description_text=request.job_description_text,
        location=request.location,
        status=ProjectStatus.DRAFT,
        candidate_count=0,
    )

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return ProjectDetailResponse(
        project_id=new_project.project_id,
        user_id=new_project.user_id,
        name=new_project.name,
        job_title=new_project.job_title,
        status=new_project.status.value,
        job_description_text=new_project.job_description_text,
        candidate_count=new_project.candidate_count,
        avg_score=new_project.avg_score,
        created_at=new_project.created_at,
        updated_at=new_project.updated_at,
        pipeline_start_time=new_project.pipeline_start_time,
        pipeline_end_time=new_project.pipeline_end_time,
        results_json=new_project.results_json,
    )


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """List all projects for authenticated user.

    Args:
        status: Optional status filter (draft, sourced, ranked, shortlisted)
        current_user: Authenticated user
        db: Database session

    Returns:
        List of projects with summaries
    """
    # Build query
    query = select(Project).where(Project.user_id == current_user.user_id)

    # Apply status filter if provided
    if status:
        try:
            status_enum = ProjectStatus(status.upper())
            query = query.where(Project.status == status_enum)
        except ValueError:
            # Invalid status, ignore filter
            pass

    query = query.order_by(Project.created_at.desc())

    # Fetch projects
    result = await db.execute(query)
    projects = result.scalars().all()

    # Convert to summaries (truncate job description)
    project_summaries = []
    for project in projects:
        # Truncate job description to first 200 chars
        truncated_jd = project.job_description_text[:200]
        if len(project.job_description_text) > 200:
            truncated_jd += "..."

        summary = ProjectSummary(
            project_id=project.project_id,
            name=project.name,
            job_title=project.job_title,
            status=project.status.value,
            job_description_text=truncated_jd,
            candidate_count=project.candidate_count,
            avg_score=project.avg_score,
            created_at=project.created_at,
            updated_at=project.updated_at,
            pipeline_start_time=project.pipeline_start_time,
            pipeline_end_time=project.pipeline_end_time,
        )
        project_summaries.append(summary)

    return ProjectListResponse(
        projects=project_summaries,
        total=len(project_summaries),
    )


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ProjectDetailResponse:
    """Get detailed project information.

    Args:
        project_id: Project ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Detailed project information

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
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

    return ProjectDetailResponse(
        project_id=project.project_id,
        user_id=project.user_id,
        name=project.name,
        job_title=project.job_title,
        status=project.status.value,
        job_description_text=project.job_description_text,
        candidate_count=project.candidate_count,
        avg_score=project.avg_score,
        created_at=project.created_at,
        updated_at=project.updated_at,
        pipeline_start_time=project.pipeline_start_time,
        pipeline_end_time=project.pipeline_end_time,
        results_json=project.results_json,
    )


@router.delete("/{project_id}")
async def delete_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Delete a project.

    Args:
        project_id: Project ID to delete
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
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
            detail="Not authorized to delete this project",
        )

    # Delete project
    await db.delete(project)
    await db.commit()

    return {"message": "Project deleted successfully"}


@router.post("/{project_id}/reset")
async def reset_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Reset project to DRAFT status and clear results.

    Args:
        project_id: Project ID to reset
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
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
            detail="Not authorized to reset this project",
        )

    # Reset project
    project.status = ProjectStatus.DRAFT
    project.candidate_count = 0
    project.avg_score = None
    project.results_json = None
    project.pipeline_start_time = None
    project.pipeline_end_time = None
    project.updated_at = datetime.utcnow()

    await db.commit()

    return {"message": "Project reset to draft successfully"}


@router.get("/{project_id}/export")
async def export_project(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> JSONResponse:
    """Export project results as JSON file.

    Args:
        project_id: Project ID to export
        current_user: Authenticated user
        db: Database session

    Returns:
        JSON file download

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
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
            detail="Not authorized to export this project",
        )

    # Return results as downloadable JSON
    return JSONResponse(
        content=project.results_json or {},
        headers={
            "Content-Disposition": f"attachment; filename=project_{project_id}.json"
        },
    )


# ============================================================================
# Multi-Stage Workflow Endpoints
# ============================================================================


@router.post("/{project_id}/source", response_model=SourceCandidatesResponse)
async def source_candidates(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> SourceCandidatesResponse:
    """Source candidates for a project (Stage 1).

    Args:
        project_id: Project ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Sourced candidates list

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 400 if invalid status
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

    # Verify status is DRAFT
    if project.status != ProjectStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only source candidates from DRAFT projects. Current status: {project.status.value}",
        )

    # Update status to SOURCING
    project.status = ProjectStatus.SOURCING
    project.pipeline_start_time = datetime.utcnow()
    project.updated_at = datetime.utcnow()
    await db.commit()

    try:
        logger.info(f"Starting sourcing for project {project_id}")
        # Import and run sourcing logic
        from src.jd_parser.parser import JDParser
        from src.github_sourcer.services.search_service import SearchService

        # Parse job description
        logger.info("Parsing job description")
        jd_parser = JDParser()
        job_req = jd_parser.parse(project.job_description_text)
        logger.info(f"Job req parsed: {job_req.role if hasattr(job_req, 'role') else 'unknown'}")

        # Inject location from project if available
        if project.location:
            logger.info(f"Injecting location from project: {project.location}")
            if not job_req.location_preferences:
                job_req.location_preferences = []
            # Add project location as first preference
            if project.location not in job_req.location_preferences:
                job_req.location_preferences.insert(0, project.location)
            logger.info(f"Location preferences after injection: {job_req.location_preferences}")

        # Source candidates from GitHub
        logger.info("Starting GitHub search")
        search_service = SearchService()
        search_result = await search_service.search(job_req)
        logger.info(f"Search completed, got {len(search_result.get('candidates', []))} candidates")

        # Extract candidates from search result (Candidate objects)
        candidates = search_result.get("candidates", [])
        logger.info(f"Extracted {len(candidates)} candidates")

        # Convert job_req and candidates to dict for storage
        # Use model_dump with mode='json' and by_alias to properly serialize all fields including HttpUrl
        import json
        from pydantic import BaseModel

        # Custom JSON encoder for Pydantic models
        def pydantic_encoder(obj):
            if isinstance(obj, BaseModel):
                return obj.model_dump(mode='json')
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

        # Serialize candidates properly
        candidates_json_str = json.dumps(
            [c.model_dump(mode='json') for c in candidates],
            default=pydantic_encoder
        )
        candidates_dicts = json.loads(candidates_json_str)

        # Serialize job requirement
        job_req_json_str = json.dumps(
            job_req.model_dump(mode='json'),
            default=pydantic_encoder
        )
        job_req_dict = json.loads(job_req_json_str)

        # Update project with results
        project.status = ProjectStatus.SOURCED
        project.candidate_count = len(candidates)
        project.results_json = {
            "candidates": candidates_dicts,
            "job_req": job_req_dict
        }
        project.pipeline_end_time = datetime.utcnow()
        project.updated_at = datetime.utcnow()

        logger.info(f"About to commit: status={project.status}, count={project.candidate_count}")
        await db.commit()
        await db.refresh(project)
        logger.info(f"After commit: status={project.status}, count={project.candidate_count}")

        return SourceCandidatesResponse(
            project_id=project.project_id,
            status=project.status.value,
            candidates=candidates_dicts,
            candidate_count=len(candidates),
        )
    except Exception as e:
        # Mark as failed
        project.status = ProjectStatus.FAILED
        project.pipeline_end_time = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        await db.commit()

        # Log full traceback for debugging
        import traceback
        logger.error(f"Sourcing failed with exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sourcing failed: {str(e)}",
        )


@router.post("/{project_id}/rank", response_model=RankCandidatesResponse)
async def rank_candidates(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RankCandidatesResponse:
    """Rank candidates for a project (Stage 2).

    Args:
        project_id: Project ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Ranked candidates list

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 400 if invalid status
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

    # Verify status is SOURCED
    if project.status != ProjectStatus.SOURCED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only rank candidates from SOURCED projects. Current status: {project.status.value}",
        )

    # Get candidates from results_json
    candidates = project.results_json.get("candidates", []) if project.results_json else []

    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No candidates to rank. Run sourcing first.",
        )

    # Update status to RANKING
    project.status = ProjectStatus.RANKING
    project.updated_at = datetime.utcnow()
    await db.commit()

    try:
        # Import and run ranking logic
        from src.ranking_engine.ranker import Ranker
        from src.jd_parser.models import JobRequirement
        from src.github_sourcer.models.candidate import Candidate

        logger.info(f"Starting ranking for project {project_id}")

        # Get job_req from results
        job_req_dict = project.results_json.get("job_req", {})
        job_req = JobRequirement(**job_req_dict)

        # Convert candidate dicts to Candidate objects
        candidate_objs = [Candidate(**c) for c in candidates]
        logger.info(f"Converting {len(candidates)} candidates to Candidate objects")

        # Rank candidates (returns list of RankedCandidate objects)
        ranker = Ranker()
        ranked_candidates_objs = ranker.rank(candidate_objs, job_req)
        logger.info(f"Ranking complete: {len(ranked_candidates_objs)} candidates ranked")

        # Flatten for API response
        ranked_candidates_dicts = [rc.flatten_for_api() for rc in ranked_candidates_objs]
        logger.info(f"Flattened {len(ranked_candidates_dicts)} ranked candidates")

        # Calculate average score
        avg_score = (
            sum(rc.total_score for rc in ranked_candidates_objs) / len(ranked_candidates_objs)
            if ranked_candidates_objs
            else 0.0
        )
        logger.info(f"Average score: {avg_score}")

        # Update project - create a new dict to ensure SQLAlchemy detects the change
        updated_results = dict(project.results_json) if project.results_json else {}
        updated_results["ranked_candidates"] = ranked_candidates_dicts

        project.status = ProjectStatus.RANKED
        project.avg_score = avg_score
        project.results_json = updated_results
        project.updated_at = datetime.utcnow()

        logger.info(f"About to commit: status={project.status}, avg_score={avg_score}, ranked_count={len(ranked_candidates_dicts)}")
        await db.commit()
        await db.refresh(project)
        logger.info(f"After commit: status={project.status}, has_ranked={bool(project.results_json.get('ranked_candidates'))}")

        return RankCandidatesResponse(
            project_id=project.project_id,
            status=project.status.value,
            ranked_candidates=ranked_candidates_dicts,
            avg_score=avg_score,
        )
    except Exception as e:
        # Mark as failed
        project.status = ProjectStatus.FAILED
        project.updated_at = datetime.utcnow()
        await db.commit()

        # Log full traceback for debugging
        import traceback
        logger.error(f"Ranking failed with exception: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ranking failed: {str(e)}",
        )


@router.post("/{project_id}/shortlist", response_model=ShortlistCandidatesResponse)
async def shortlist_candidates(
    project_id: str,
    request: ShortlistCandidatesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ShortlistCandidatesResponse:
    """Shortlist selected candidates (Stage 3).

    Args:
        project_id: Project ID
        request: List of candidate usernames to shortlist
        current_user: Authenticated user
        db: Database session

    Returns:
        Shortlisting confirmation

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 400 if invalid status
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

    # Verify status is RANKED
    if project.status != ProjectStatus.RANKED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only shortlist from RANKED projects. Current status: {project.status.value}",
        )

    # Get ranked candidates
    ranked_candidates = project.results_json.get("ranked_candidates", []) if project.results_json else []

    # Find candidates to shortlist
    candidates_to_shortlist = [
        c for c in ranked_candidates
        if c.get("github_username") in request.candidate_usernames
    ]

    if len(candidates_to_shortlist) != len(request.candidate_usernames):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some candidates not found in ranked list",
        )

    # Create shortlist entries
    for candidate in candidates_to_shortlist:
        # Check if already shortlisted
        existing = await db.execute(
            select(ShortlistedCandidate)
            .where(ShortlistedCandidate.project_id == project_id)
            .where(ShortlistedCandidate.github_username == candidate["github_username"])
        )
        if existing.scalars().first():
            continue  # Skip if already shortlisted

        shortlisted = ShortlistedCandidate(
            project_id=project_id,
            github_username=candidate["github_username"],
            candidate_data=candidate,
        )
        db.add(shortlisted)

    # Update project status
    project.status = ProjectStatus.SHORTLISTED
    project.updated_at = datetime.utcnow()

    await db.commit()

    # Count shortlisted
    count_result = await db.execute(
        select(func.count()).select_from(ShortlistedCandidate).where(ShortlistedCandidate.project_id == project_id)
    )
    shortlisted_count = count_result.scalar()

    return ShortlistCandidatesResponse(
        project_id=project.project_id,
        status=project.status.value,
        shortlisted_count=shortlisted_count,
    )


@router.get("/{project_id}/shortlist", response_model=list[ShortlistedCandidateResponse])
async def get_shortlist(
    project_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ShortlistedCandidateResponse]:
    """Get shortlisted candidates for a project.

    Args:
        project_id: Project ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of shortlisted candidates

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
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

    # Get shortlisted candidates
    shortlist_result = await db.execute(
        select(ShortlistedCandidate)
        .where(ShortlistedCandidate.project_id == project_id)
        .order_by(ShortlistedCandidate.created_at.desc())
    )
    shortlisted = shortlist_result.scalars().all()

    return [
        ShortlistedCandidateResponse(
            shortlist_id=s.shortlist_id,
            project_id=s.project_id,
            github_username=s.github_username,
            candidate_data=s.candidate_data,
            enriched_data=s.enriched_data,
            enrichment_status=s.enrichment_status.value,
            enriched_at=s.enriched_at,
            created_at=s.created_at,
        )
        for s in shortlisted
    ]


@router.post("/{project_id}/shortlist/{github_username}/toggle", response_model=ToggleShortlistResponse)
async def toggle_shortlist(
    project_id: str,
    github_username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ToggleShortlistResponse:
    """Toggle shortlist status for a single candidate.

    Args:
        project_id: Project ID
        github_username: GitHub username to toggle
        current_user: Authenticated user
        db: Database session

    Returns:
        Toggle confirmation with new status

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 400 if candidate not ranked
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

    # Must be ranked or already shortlisted
    if project.status not in [ProjectStatus.RANKED, ProjectStatus.SHORTLISTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Can only shortlist from RANKED or SHORTLISTED projects. Current status: {project.status.value}",
        )

    # Get ranked candidates
    ranked_candidates = project.results_json.get("ranked_candidates", []) if project.results_json else []
    candidate_data = next((c for c in ranked_candidates if c.get("github_username") == github_username), None)

    if not candidate_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not found in ranked list",
        )

    # Check if already shortlisted
    existing = await db.execute(
        select(ShortlistedCandidate)
        .where(ShortlistedCandidate.project_id == project_id)
        .where(ShortlistedCandidate.github_username == github_username)
    )
    existing_shortlist = existing.scalars().first()

    if existing_shortlist:
        # Remove from shortlist
        await db.delete(existing_shortlist)
        is_shortlisted = False
    else:
        # Add to shortlist
        shortlisted = ShortlistedCandidate(
            project_id=project_id,
            github_username=github_username,
            candidate_data=candidate_data,
        )
        db.add(shortlisted)
        is_shortlisted = True

        # Update project status to SHORTLISTED on first shortlist
        if project.status == ProjectStatus.RANKED:
            project.status = ProjectStatus.SHORTLISTED
            project.updated_at = datetime.utcnow()

    await db.commit()

    # Count shortlisted
    count_result = await db.execute(
        select(func.count()).select_from(ShortlistedCandidate).where(ShortlistedCandidate.project_id == project_id)
    )
    shortlisted_count = count_result.scalar()

    return ToggleShortlistResponse(
        project_id=project_id,
        github_username=github_username,
        is_shortlisted=is_shortlisted,
        shortlisted_count=shortlisted_count,
    )


@router.post("/{project_id}/shortlist/{github_username}/enrich", response_model=EnrichCandidateResponse)
async def enrich_candidate(
    project_id: str,
    github_username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> EnrichCandidateResponse:
    """Enrich a shortlisted candidate with contact information (Module 010).

    Args:
        project_id: Project ID
        github_username: GitHub username to enrich
        current_user: Authenticated user
        db: Database session

    Returns:
        Enriched candidate data

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 500 if enrichment fails
    """
    import traceback
    import os
    from src.backend_api.models import EnrichmentStatus

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

    # Find shortlisted candidate
    shortlist_result = await db.execute(
        select(ShortlistedCandidate)
        .where(ShortlistedCandidate.project_id == project_id)
        .where(ShortlistedCandidate.github_username == github_username)
    )
    shortlisted = shortlist_result.scalars().first()

    if not shortlisted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not in shortlist. Shortlist them first.",
        )

    # Check if already enriched
    if shortlisted.enrichment_status == EnrichmentStatus.COMPLETED:
        logger.info(f"Candidate {github_username} already enriched, returning cached data")
        return EnrichCandidateResponse(
            shortlist_id=shortlisted.shortlist_id,
            github_username=shortlisted.github_username,
            enrichment_status=shortlisted.enrichment_status.value,
            enriched_data=shortlisted.enriched_data or {},
            enriched_at=shortlisted.enriched_at,
        )

    # Update status to in_progress
    shortlisted.enrichment_status = EnrichmentStatus.IN_PROGRESS
    await db.commit()

    try:
        logger.info(f"Starting enrichment for {github_username}")

        # Get GitHub token from environment
        github_token = os.getenv("GITHUB_TOKEN", "test_token")

        # Import contact enricher
        from src.contact_enrichment import ContactEnricher

        # Create enricher instance
        enricher = ContactEnricher(github_token=github_token, retention_days=30)

        # Prepare candidate data for enrichment
        candidate_data = shortlisted.candidate_data.copy()
        candidate_data["github_username"] = github_username

        # Enrich with fetch_fresh=True to get real GitHub data
        logger.info(f"Calling enricher.enrich() with fetch_fresh=True")
        contact_info = await enricher.enrich(candidate_data, fetch_fresh=True)

        # Convert ContactInfo to dict for storage
        enriched_data = {
            "primary_email": contact_info.primary_email,
            "additional_emails": contact_info.additional_emails,
            "linkedin_username": contact_info.linkedin_username,
            "twitter_username": contact_info.twitter_username,
            "blog_url": contact_info.blog_url,
            "company": contact_info.company,
            "hireable": contact_info.hireable,
            "contact_sources": contact_info.contact_sources,
            "enriched_at": contact_info.enriched_at.isoformat(),
            "gdpr_collection_basis": contact_info.gdpr_collection_basis,
            "data_retention_expires_at": contact_info.data_retention_expires_at.isoformat(),
        }

        logger.info(f"Enrichment successful, found {len(contact_info.contact_sources)} contact sources")

        # Update shortlist entry
        shortlisted.enriched_data = enriched_data
        shortlisted.enrichment_status = EnrichmentStatus.COMPLETED
        shortlisted.enriched_at = datetime.utcnow()
        await db.commit()
        await db.refresh(shortlisted)

        return EnrichCandidateResponse(
            shortlist_id=shortlisted.shortlist_id,
            github_username=shortlisted.github_username,
            enrichment_status=shortlisted.enrichment_status.value,
            enriched_data=enriched_data,
            enriched_at=shortlisted.enriched_at,
        )

    except Exception as e:
        # Mark as failed
        shortlisted.enrichment_status = EnrichmentStatus.FAILED
        await db.commit()

        # Log full traceback
        logger.error(f"Enrichment failed for {github_username}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Enrichment failed: {str(e)}",
        )


# ============================================================================
# Module 004: Outreach Generator Endpoints
# ============================================================================


@router.post("/{project_id}/shortlist/{github_username}/outreach", response_model=GenerateOutreachResponse)
async def generate_outreach(
    project_id: str,
    github_username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GenerateOutreachResponse:
    """Generate personalized outreach messages for a shortlisted candidate (Module 004).

    Generates multi-channel outreach (email, LinkedIn, Twitter) using the 3-stage
    LLM pipeline (Analysis → Generation → Refinement) with personalization scoring,
    cliché detection, and token tracking.

    Args:
        project_id: Project ID
        github_username: GitHub username of shortlisted candidate
        current_user: Authenticated user
        db: Database session

    Returns:
        Generated outreach messages (1-3 channels depending on available contact info)

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 400 if not enriched, 500 if generation fails
    """
    import traceback
    import os

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

    # Find shortlisted candidate
    shortlist_result = await db.execute(
        select(ShortlistedCandidate)
        .where(ShortlistedCandidate.project_id == project_id)
        .where(ShortlistedCandidate.github_username == github_username)
    )
    shortlisted = shortlist_result.scalars().first()

    if not shortlisted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not in shortlist. Shortlist them first.",
        )

    # Verify candidate is enriched
    from src.backend_api.models import EnrichmentStatus
    if shortlisted.enrichment_status != EnrichmentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Candidate must be enriched before generating outreach. Call /enrich first.",
        )

    try:
        logger.info(f"Starting outreach generation for {github_username}")

        # Import outreach orchestrator
        from src.outreach_generator.orchestrator import OutreachOrchestrator
        from src.jd_parser.models import JobRequirement
        from src.backend_api.models import OutreachStatus

        # Get job requirement from project
        job_req_dict = project.results_json.get("job_req", {}) if project.results_json else {}
        job_req = JobRequirement(**job_req_dict)

        # Get candidate data
        candidate_data = shortlisted.candidate_data

        # Get enrichment data
        enrichment = shortlisted.enriched_data or {}

        # Get LLM client from environment
        llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
        api_key = os.getenv("ANTHROPIC_API_KEY") if llm_provider == "anthropic" else os.getenv("OPENAI_API_KEY")

        if llm_provider == "anthropic":
            from src.jd_parser.llm_client import AnthropicClient
            llm_client = AnthropicClient(api_key=api_key)
        else:
            from src.jd_parser.llm_client import OpenAIClient
            llm_client = OpenAIClient(api_key=api_key)

        # Create orchestrator
        orchestrator = OutreachOrchestrator(llm_client=llm_client)

        # Generate outreach messages
        logger.info("Calling OutreachOrchestrator.generate_outreach()")
        outreach_messages = orchestrator.generate_outreach(
            candidate=candidate_data,
            job_req=job_req.model_dump(),
            enrichment=enrichment
        )

        logger.info(f"Generated {len(outreach_messages)} outreach messages")

        # Save to database
        saved_messages = []
        for msg in outreach_messages:
            # Check if message already exists for this channel
            existing = await db.execute(
                select(OutreachMessage)
                .where(OutreachMessage.project_id == project_id)
                .where(OutreachMessage.github_username == github_username)
                .where(OutreachMessage.channel == msg.channel)
            )
            existing_msg = existing.scalars().first()

            if existing_msg:
                # Delete existing message (regenerate)
                await db.delete(existing_msg)
                await db.flush()

            # Create new outreach message
            outreach_db = OutreachMessage(
                project_id=project_id,
                github_username=github_username,
                channel=msg.channel,
                subject_line=msg.subject_line,
                message_text=msg.message_text,
                personalization_score=msg.personalization_score,
                personalization_metadata=msg.personalization_metadata.model_dump(),
                tokens_used=msg.tokens_used,
                stage_breakdown=msg.stage_breakdown,
                is_edited=False,
                status=OutreachStatus.DRAFT,
            )
            db.add(outreach_db)
            await db.flush()
            await db.refresh(outreach_db)

            saved_messages.append(OutreachMessageResponse(
                outreach_id=outreach_db.outreach_id,
                project_id=outreach_db.project_id,
                github_username=outreach_db.github_username,
                channel=outreach_db.channel.value,
                subject_line=outreach_db.subject_line,
                message_text=outreach_db.message_text,
                personalization_score=outreach_db.personalization_score,
                personalization_metadata=outreach_db.personalization_metadata,
                tokens_used=outreach_db.tokens_used,
                stage_breakdown=outreach_db.stage_breakdown,
                is_edited=outreach_db.is_edited,
                edited_message=outreach_db.edited_message,
                edited_at=outreach_db.edited_at,
                status=outreach_db.status.value,
                sent_at=outreach_db.sent_at,
                generated_at=outreach_db.generated_at,
            ))

        await db.commit()

        logger.info(f"Saved {len(saved_messages)} outreach messages to database")

        return GenerateOutreachResponse(
            project_id=project_id,
            github_username=github_username,
            messages=saved_messages,
        )

    except Exception as e:
        await db.rollback()

        # Log full traceback
        logger.error(f"Outreach generation failed for {github_username}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Outreach generation failed: {str(e)}",
        )


@router.get("/{project_id}/shortlist/{github_username}/outreach", response_model=list[OutreachMessageResponse])
async def get_outreach(
    project_id: str,
    github_username: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[OutreachMessageResponse]:
    """Get existing outreach messages for a shortlisted candidate (Module 004).

    Args:
        project_id: Project ID
        github_username: GitHub username
        current_user: Authenticated user
        db: Database session

    Returns:
        List of outreach messages (up to 3 channels)

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
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

    # Get outreach messages
    outreach_result = await db.execute(
        select(OutreachMessage)
        .where(OutreachMessage.project_id == project_id)
        .where(OutreachMessage.github_username == github_username)
        .order_by(OutreachMessage.generated_at.desc())
    )
    messages = outreach_result.scalars().all()

    return [
        OutreachMessageResponse(
            outreach_id=msg.outreach_id,
            project_id=msg.project_id,
            github_username=msg.github_username,
            channel=msg.channel.value,
            subject_line=msg.subject_line,
            message_text=msg.message_text,
            personalization_score=msg.personalization_score,
            personalization_metadata=msg.personalization_metadata,
            tokens_used=msg.tokens_used,
            stage_breakdown=msg.stage_breakdown,
            is_edited=msg.is_edited,
            edited_message=msg.edited_message,
            edited_at=msg.edited_at,
            status=msg.status.value,
            sent_at=msg.sent_at,
            generated_at=msg.generated_at,
        )
        for msg in messages
    ]


@router.put("/{project_id}/shortlist/{github_username}/outreach/{message_id}", response_model=OutreachMessageResponse)
async def update_outreach(
    project_id: str,
    github_username: str,
    message_id: str,
    request: UpdateOutreachRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> OutreachMessageResponse:
    """Update (edit) an outreach message (Module 004).

    Args:
        project_id: Project ID
        github_username: GitHub username
        message_id: Outreach message ID
        request: Updated message text
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated outreach message

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
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

    # Find outreach message
    msg_result = await db.execute(
        select(OutreachMessage)
        .where(OutreachMessage.outreach_id == message_id)
        .where(OutreachMessage.project_id == project_id)
        .where(OutreachMessage.github_username == github_username)
    )
    message = msg_result.scalars().first()

    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach message not found",
        )

    # Update message
    message.edited_message = request.message_text
    message.is_edited = True
    message.edited_at = datetime.utcnow()

    await db.commit()
    await db.refresh(message)

    return OutreachMessageResponse(
        outreach_id=message.outreach_id,
        project_id=message.project_id,
        github_username=message.github_username,
        channel=message.channel.value,
        subject_line=message.subject_line,
        message_text=message.message_text,
        personalization_score=message.personalization_score,
        personalization_metadata=message.personalization_metadata,
        tokens_used=message.tokens_used,
        stage_breakdown=message.stage_breakdown,
        is_edited=message.is_edited,
        edited_message=message.edited_message,
        edited_at=message.edited_at,
        status=message.status.value,
        sent_at=message.sent_at,
        generated_at=message.generated_at,
    )


@router.post("/{project_id}/shortlist/{github_username}/outreach/{message_id}/regenerate", response_model=RegenerateOutreachResponse)
async def regenerate_outreach(
    project_id: str,
    github_username: str,
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RegenerateOutreachResponse:
    """Regenerate an outreach message for a specific channel (Module 004).

    Deletes the existing message and generates a new one for the same channel.

    Args:
        project_id: Project ID
        github_username: GitHub username
        message_id: Outreach message ID to regenerate
        current_user: Authenticated user
        db: Database session

    Returns:
        Regenerated outreach message

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 500 if regeneration fails
    """
    import traceback
    import os

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

    # Find existing message
    msg_result = await db.execute(
        select(OutreachMessage)
        .where(OutreachMessage.outreach_id == message_id)
        .where(OutreachMessage.project_id == project_id)
        .where(OutreachMessage.github_username == github_username)
    )
    existing_message = msg_result.scalars().first()

    if not existing_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach message not found",
        )

    # Store channel before deleting
    channel = existing_message.channel

    # Find shortlisted candidate
    shortlist_result = await db.execute(
        select(ShortlistedCandidate)
        .where(ShortlistedCandidate.project_id == project_id)
        .where(ShortlistedCandidate.github_username == github_username)
    )
    shortlisted = shortlist_result.scalars().first()

    if not shortlisted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not in shortlist",
        )

    try:
        logger.info(f"Regenerating {channel.value} outreach for {github_username}")

        # Delete existing message
        await db.delete(existing_message)
        await db.flush()

        # Import outreach orchestrator
        from src.outreach_generator.orchestrator import OutreachOrchestrator
        from src.jd_parser.models import JobRequirement
        from src.backend_api.models import OutreachStatus

        # Get job requirement from project
        job_req_dict = project.results_json.get("job_req", {}) if project.results_json else {}
        job_req = JobRequirement(**job_req_dict)

        # Get candidate and enrichment data
        candidate_data = shortlisted.candidate_data
        enrichment = shortlisted.enriched_data or {}

        # Get LLM client
        llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
        api_key = os.getenv("ANTHROPIC_API_KEY") if llm_provider == "anthropic" else os.getenv("OPENAI_API_KEY")

        if llm_provider == "anthropic":
            from src.jd_parser.llm_client import AnthropicClient
            llm_client = AnthropicClient(api_key=api_key)
        else:
            from src.jd_parser.llm_client import OpenAIClient
            llm_client = OpenAIClient(api_key=api_key)

        # Create orchestrator
        orchestrator = OutreachOrchestrator(llm_client=llm_client)

        # Generate new messages
        outreach_messages = orchestrator.generate_outreach(
            candidate=candidate_data,
            job_req=job_req.model_dump(),
            enrichment=enrichment
        )

        # Find message for the same channel
        new_msg = next((m for m in outreach_messages if m.channel == channel), None)

        if not new_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot generate {channel.value} message - contact info not available",
            )

        # Save to database
        outreach_db = OutreachMessage(
            project_id=project_id,
            github_username=github_username,
            channel=new_msg.channel,
            subject_line=new_msg.subject_line,
            message_text=new_msg.message_text,
            personalization_score=new_msg.personalization_score,
            personalization_metadata=new_msg.personalization_metadata.model_dump(),
            tokens_used=new_msg.tokens_used,
            stage_breakdown=new_msg.stage_breakdown,
            is_edited=False,
            status=OutreachStatus.DRAFT,
        )
        db.add(outreach_db)
        await db.commit()
        await db.refresh(outreach_db)

        logger.info(f"Regenerated {channel.value} outreach message")

        return RegenerateOutreachResponse(
            project_id=project_id,
            github_username=github_username,
            channel=channel.value,
            message=OutreachMessageResponse(
                outreach_id=outreach_db.outreach_id,
                project_id=outreach_db.project_id,
                github_username=outreach_db.github_username,
                channel=outreach_db.channel.value,
                subject_line=outreach_db.subject_line,
                message_text=outreach_db.message_text,
                personalization_score=outreach_db.personalization_score,
                personalization_metadata=outreach_db.personalization_metadata,
                tokens_used=outreach_db.tokens_used,
                stage_breakdown=outreach_db.stage_breakdown,
                is_edited=outreach_db.is_edited,
                edited_message=outreach_db.edited_message,
                edited_at=outreach_db.edited_at,
                status=outreach_db.status.value,
                sent_at=outreach_db.sent_at,
                generated_at=outreach_db.generated_at,
            ),
        )

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()

        # Log full traceback
        logger.error(f"Outreach regeneration failed for {github_username}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Outreach regeneration failed: {str(e)}",
        )


@router.post("/{project_id}/shortlist/{github_username}/outreach/{message_id}/follow-ups", response_model=GenerateFollowUpsResponse)
async def generate_follow_ups(
    project_id: str,
    github_username: str,
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GenerateFollowUpsResponse:
    """Generate 3-part follow-up sequence for an outreach message (Module 004).

    Generates:
    - Day 3: Reminder (different repo mention)
    - Day 7: Technical Challenge (problem preview)
    - Day 14: Soft Close (gentle opt-out)

    Args:
        project_id: Project ID
        github_username: GitHub username
        message_id: Outreach message ID
        current_user: Authenticated user
        db: Database session

    Returns:
        3-part follow-up sequence

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized, 500 if generation fails
    """
    import traceback
    import os

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

    # Find outreach message
    msg_result = await db.execute(
        select(OutreachMessage)
        .where(OutreachMessage.outreach_id == message_id)
        .where(OutreachMessage.project_id == project_id)
        .where(OutreachMessage.github_username == github_username)
    )
    outreach_message = msg_result.scalars().first()

    if not outreach_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach message not found",
        )

    # Find shortlisted candidate
    shortlist_result = await db.execute(
        select(ShortlistedCandidate)
        .where(ShortlistedCandidate.project_id == project_id)
        .where(ShortlistedCandidate.github_username == github_username)
    )
    shortlisted = shortlist_result.scalars().first()

    if not shortlisted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Candidate not in shortlist",
        )

    try:
        logger.info(f"Generating follow-ups for {github_username}")

        # Delete existing follow-ups for this message
        await db.execute(
            FollowUpSequence.__table__.delete().where(
                FollowUpSequence.outreach_message_id == message_id
            )
        )
        await db.flush()

        # Import follow-up generator
        from src.outreach_generator.follow_up_generator import FollowUpGenerator
        from src.jd_parser.models import JobRequirement
        from src.outreach_generator.models import OutreachMessage as OutreachMessageModel

        # Get job requirement
        job_req_dict = project.results_json.get("job_req", {}) if project.results_json else {}
        job_req = JobRequirement(**job_req_dict)

        # Get candidate data
        candidate_data = shortlisted.candidate_data

        # Get LLM client
        llm_provider = os.getenv("LLM_PROVIDER", "anthropic")
        api_key = os.getenv("ANTHROPIC_API_KEY") if llm_provider == "anthropic" else os.getenv("OPENAI_API_KEY")

        if llm_provider == "anthropic":
            from src.jd_parser.llm_client import AnthropicClient
            llm_client = AnthropicClient(api_key=api_key)
        else:
            from src.jd_parser.llm_client import OpenAIClient
            llm_client = OpenAIClient(api_key=api_key)

        # Create follow-up generator
        generator = FollowUpGenerator(llm_client=llm_client)

        # Convert DB outreach message to model
        outreach_msg_model = OutreachMessageModel(
            shortlist_id=shortlisted.shortlist_id,
            channel=outreach_message.channel,
            subject_line=outreach_message.subject_line,
            message_text=outreach_message.message_text,
            personalization_score=outreach_message.personalization_score,
            personalization_metadata=outreach_message.personalization_metadata,
            tokens_used=outreach_message.tokens_used,
            stage_breakdown=outreach_message.stage_breakdown,
            is_edited=outreach_message.is_edited,
            generated_at=outreach_message.generated_at,
            edited_at=outreach_message.edited_at,
        )

        # Generate follow-ups
        follow_ups = generator.generate_sequence(
            outreach_message=outreach_msg_model,
            job_req=job_req.model_dump(),
            candidate=candidate_data
        )

        logger.info(f"Generated {len(follow_ups)} follow-ups")

        # Save to database
        saved_follow_ups = []
        for followup in follow_ups:
            followup_db = FollowUpSequence(
                outreach_message_id=message_id,
                sequence_number=followup.sequence_number,
                scheduled_days_after=followup.scheduled_days_after,
                message_text=followup.message_text,
                angle=followup.angle,
            )
            db.add(followup_db)
            await db.flush()
            await db.refresh(followup_db)

            saved_follow_ups.append(FollowUpSequenceResponse(
                followup_id=followup_db.followup_id,
                outreach_message_id=followup_db.outreach_message_id,
                sequence_number=followup_db.sequence_number,
                scheduled_days_after=followup_db.scheduled_days_after,
                message_text=followup_db.message_text,
                angle=followup_db.angle.value,
                generated_at=followup_db.generated_at,
                sent_at=followup_db.sent_at,
            ))

        await db.commit()

        logger.info(f"Saved {len(saved_follow_ups)} follow-ups to database")

        return GenerateFollowUpsResponse(
            outreach_message_id=message_id,
            follow_ups=saved_follow_ups,
        )

    except Exception as e:
        await db.rollback()

        # Log full traceback
        logger.error(f"Follow-up generation failed for {github_username}: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Follow-up generation failed: {str(e)}",
        )


@router.get("/{project_id}/shortlist/{github_username}/outreach/{message_id}/follow-ups", response_model=list[FollowUpSequenceResponse])
async def get_follow_ups(
    project_id: str,
    github_username: str,
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FollowUpSequenceResponse]:
    """Get follow-up sequences for an outreach message (Module 004).

    Args:
        project_id: Project ID
        github_username: GitHub username
        message_id: Outreach message ID
        current_user: Authenticated user
        db: Database session

    Returns:
        List of follow-up sequences

    Raises:
        HTTPException: 404 if not found, 403 if unauthorized
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

    # Verify outreach message exists and belongs to this project
    msg_result = await db.execute(
        select(OutreachMessage)
        .where(OutreachMessage.outreach_id == message_id)
        .where(OutreachMessage.project_id == project_id)
        .where(OutreachMessage.github_username == github_username)
    )
    outreach_message = msg_result.scalars().first()

    if not outreach_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Outreach message not found",
        )

    # Get follow-ups
    followups_result = await db.execute(
        select(FollowUpSequence)
        .where(FollowUpSequence.outreach_message_id == message_id)
        .order_by(FollowUpSequence.sequence_number.asc())
    )
    followups = followups_result.scalars().all()

    return [
        FollowUpSequenceResponse(
            followup_id=f.followup_id,
            outreach_message_id=f.outreach_message_id,
            sequence_number=f.sequence_number,
            scheduled_days_after=f.scheduled_days_after,
            message_text=f.message_text,
            angle=f.angle.value,
            generated_at=f.generated_at,
            sent_at=f.sent_at,
        )
        for f in followups
    ]
