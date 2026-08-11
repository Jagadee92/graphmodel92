# This file contains the simple security functions used in the project.

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.core.config import get_settings


# This reads the Bearer token from the Authorization header.
bearer = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    # Convert the password into bytes because bcrypt needs bytes.
    password_bytes = password.encode("utf-8")

    # Create a secure hash of the password.
    hashed_password = bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt()
    )

    # Convert the hash back to a string so we can save it in the database.
    return hashed_password.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    # Convert both values into bytes.
    password_bytes = password.encode("utf-8")
    hash_bytes = password_hash.encode("utf-8")

    # bcrypt checks whether the password matches the saved hash.
    return bcrypt.checkpw(password_bytes, hash_bytes)


def create_token(candidate_id: str, email: str) -> str:
    # Get JWT settings from the .env file.
    settings = get_settings()

    # Get the current UTC time.
    current_time = datetime.now(timezone.utc)

    # These values are stored inside the JWT.
    payload = {
        "sub": candidate_id,
        "email": email,
        "iat": current_time,
        "exp": current_time + timedelta(
            minutes=settings.jwt_expire_minutes
        ),
    }

    # Create and return the JWT token.
    token = jwt.encode(
        payload,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm
    )

    return token


def verify_token(token: str) -> str:
    # Get JWT settings.
    settings = get_settings()

    try:
        # Decode the token and check its signature and expiration.
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        # The candidate id is stored in the "sub" field.
        candidate_id = payload.get("sub")

        if not candidate_id:
            raise ValueError("Candidate id is missing")

        return candidate_id

    except (JWTError, ValueError):
        # This is returned when the token is invalid or expired.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def get_current_candidate_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer)
) -> str:
    # Check whether the request contains a Bearer token.
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

    # Send the token to verify_token().
    return verify_token(credentials.credentials)
