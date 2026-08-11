from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.profile import ProfileUpdateRequest
from app.schemas.jobs import ApplyRequest
from app.core.security import (
    hash_password,
    verify_password,
    create_token,
    get_current_candidate_id,
)
from app.services import graph_service
from app.services.email_service import send_application_email


# Public routes are used before the candidate logs in.
public_router = APIRouter(prefix="/api")


@public_router.get("/health")
def health():
    try:
        from app.db.driver import verify_database_connection

        verify_database_connection()

        return {
            "status": "ok",
            "database": "connected"
        }

    except Exception as exc:
        return {
            "status": "degraded",
            "database": "unavailable",
            "detail": str(exc)
        }


@public_router.post(
    "/auth/register",
    response_model=TokenResponse,
    status_code=201
)
def register(payload: RegisterRequest):
    # First check whether this email is already registered.
    old_candidate = graph_service.candidate_by_email(
        payload.email.lower()
    )

    if old_candidate:
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists"
        )

    # Hash the password before saving it.
    password_hash = hash_password(payload.password)

    # Create the candidate in CognoDB.
    candidate = graph_service.create_candidate(
        payload.model_dump(),
        password_hash
    )

    # Give the candidate a token after registration.
    token = create_token(
        candidate["id"],
        candidate["email"]
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@public_router.post(
    "/auth/login",
    response_model=TokenResponse
)
def login(payload: LoginRequest):
    # Find the candidate using the email.
    candidate = graph_service.candidate_by_email(
        payload.email.lower()
    )

    # Check the password.
    if not candidate:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    password_is_correct = verify_password(
        payload.password,
        candidate.get("password_hash", "")
    )

    if not password_is_correct:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create a token after successful login.
    token = create_token(
        candidate["id"],
        candidate["email"]
    )

    return {
        "access_token": token,
        "token_type": "bearer"
    }


# All routers below this point require a valid JWT token.
#
# FastAPI checks get_current_candidate_id() before calling
# any endpoint in this router.
protected_router = APIRouter(
    prefix="/api",
    dependencies=[Depends(get_current_candidate_id)]
)


@protected_router.get("/me")
def me(
    candidate_id: str = Depends(get_current_candidate_id)
):
    data = graph_service.profile(candidate_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Candidate profile not found"
        )

    return data


@protected_router.put("/me")
def update_me(
    payload: ProfileUpdateRequest,
    candidate_id: str = Depends(get_current_candidate_id)
):
    graph_service.update_profile(
        candidate_id,
        payload.model_dump()
    )

    return graph_service.profile(candidate_id)


@protected_router.get("/jobs")
def jobs(
    search: str | None = None,
    skill: str | None = None
):
    return graph_service.list_jobs(search, skill)


@protected_router.get("/jobs/{job_id}")
def job(job_id: str):
    result = graph_service.job_by_id(job_id)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return result


@protected_router.get("/me/recommendations")
def my_recommendations(
    candidate_id: str = Depends(get_current_candidate_id)
):
    return graph_service.recommendations(candidate_id)


@protected_router.get("/me/applications")
def applications(
    candidate_id: str = Depends(get_current_candidate_id)
):
    data = graph_service.profile(candidate_id)

    if not data:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    return data["applications"]


@protected_router.post("/jobs/{job_id}/apply")
def apply(
    job_id: str,
    payload: ApplyRequest,
    candidate_id: str = Depends(get_current_candidate_id)
):
    # Get the logged-in candidate.
    candidate = graph_service.candidate_by_id(candidate_id)

    # Get the selected job.
    job = graph_service.job_by_id(job_id)

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Candidate not found"
        )

    if not job:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    # Do not allow the same candidate to apply twice.
    if graph_service.has_applied(candidate_id, job_id):
        reason = "You have already applied to this job."

        email_status = send_application_email(
            candidate["email"],
            candidate["name"],
            job["title"],
            "FAILED",
            reason
        )

        graph_service.create_attempt(
            candidate_id,
            job_id,
            "FAILED",
            reason,
            email_status
        )

        raise HTTPException(
            status_code=409,
            detail=reason
        )

    try:
        # Save the application.
        application = graph_service.create_application(
            candidate_id,
            job_id,
            payload.cover_note,
            "PENDING"
        )

        # Send an email after the application is saved.
        email_status = send_application_email(
            candidate["email"],
            candidate["name"],
            job["title"],
            "SUCCESS"
        )

        # Save the email notification result.
        from app.db.session import get_session

        query = """
        MATCH (c:Candidate {id:$candidate_id})
              -[a:APPLIED_TO {id:$application_id}]->(j:Job)
        SET a.email_notification = $email_status
        RETURN a
        """

        with get_session() as session:
            session.run(
                query,
                candidate_id=candidate_id,
                application_id=application["id"],
                email_status=email_status
            ).consume()

        # Save a successful application attempt.
        graph_service.create_attempt(
            candidate_id,
            job_id,
            "SUCCESS",
            "",
            email_status
        )

        return {
            "success": True,
            "message": "Application submitted successfully",
            "application_id": application["id"],
            "email_notification": email_status
        }

    except HTTPException:
        raise

    except Exception as exc:
        reason = "Application could not be submitted."

        email_status = send_application_email(
            candidate["email"],
            candidate["name"],
            job["title"],
            "FAILED",
            str(exc)
        )

        graph_service.create_attempt(
            candidate_id,
            job_id,
            "FAILED",
            str(exc),
            email_status
        )

        raise HTTPException(
            status_code=500,
            detail=reason
        )


@protected_router.get("/stats")
def statistics():
    return graph_service.stats()


@protected_router.get("/skills/{skill_name}/network")
def network(skill_name: str):
    result = graph_service.skill_network(skill_name)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Skill not found"
        )

    return result
