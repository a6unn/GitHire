"""Authentication router for user registration, login, and logout."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.backend_api.auth import hash_password, verify_password, create_access_token, get_current_user
from src.backend_api.database import get_db
from src.backend_api.models import User, Session as SessionModel, PasswordResetToken
from src.backend_api.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
    UpdateProfileRequest,
    ChangePasswordRequest,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    ResetPasswordRequest,
    MessageResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Register a new user account.

    Args:
        request: Registration request with email and password
        db: Database session

    Returns:
        Created user information

    Raises:
        HTTPException: 400 if email already exists
    """
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password
    hashed_password = hash_password(request.password)

    # Create user
    user = User(
        email=request.email,
        hashed_password=hashed_password,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    return UserResponse.model_validate(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Login to get access token.

    Args:
        request: Login request with email and password
        db: Database session

    Returns:
        JWT access token

    Raises:
        HTTPException: 401 if credentials are invalid
    """
    # Fetch user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token = create_access_token(
        data={"user_id": user.user_id, "email": user.email}
    )

    # Create session record
    session = SessionModel(
        user_id=user.user_id,
        token=access_token,
    )

    db.add(session)

    # Update last login
    from datetime import datetime
    user.last_login = datetime.utcnow()

    await db.commit()

    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Logout and invalidate session.

    Args:
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message
    """
    # Delete all sessions for this user
    result = await db.execute(
        select(SessionModel).where(SessionModel.user_id == current_user.user_id)
    )
    sessions = result.scalars().all()

    for session in sessions:
        await db.delete(session)

    await db.commit()

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserResponse:
    """Get current user profile.

    Args:
        current_user: Current authenticated user

    Returns:
        User profile information
    """
    return UserResponse.model_validate(current_user)


@router.put("/me", response_model=UserResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update user profile.

    Args:
        request: Profile update request with name
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated user profile
    """
    # Update user name
    current_user.name = request.name

    await db.commit()
    await db.refresh(current_user)

    return UserResponse.model_validate(current_user)


@router.put("/password", response_model=MessageResponse)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Change password for authenticated user.

    Args:
        request: Password change request with current and new password
        current_user: Current authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 401 if current password is incorrect
    """
    # Verify current password
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )

    # Hash and update new password
    current_user.hashed_password = hash_password(request.new_password)

    await db.commit()

    return MessageResponse(message="Password changed successfully")


@router.post("/forgot-password", response_model=ForgotPasswordResponse)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> ForgotPasswordResponse:
    """Request password reset for user account.

    Generates a password reset token that expires in 1 hour.

    NOTE: In production, this should send an email with the reset link.
    For now, it returns the token in the response for testing purposes.

    Args:
        request: Forgot password request with email
        db: Database session

    Returns:
        Success message and reset token (testing only)

    Raises:
        HTTPException: Always returns success even if email doesn't exist
        (to prevent email enumeration attacks)
    """
    import secrets
    from datetime import datetime, timedelta

    # Fetch user by email
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalars().first()

    # Always return success to prevent email enumeration
    if not user:
        return ForgotPasswordResponse(
            message="If an account exists with that email, a password reset link has been sent."
        )

    # Generate secure random token
    reset_token = secrets.token_urlsafe(32)

    # Create reset token record
    password_reset = PasswordResetToken(
        user_id=user.user_id,
        token=reset_token,
    )

    db.add(password_reset)
    await db.commit()

    # TODO: In production, send email with reset link:
    # reset_link = f"https://yourdomain.com/reset-password?token={reset_token}"
    # send_email(user.email, "Password Reset", reset_link)

    return ForgotPasswordResponse(
        message="If an account exists with that email, a password reset link has been sent.",
        reset_token=reset_token,  # Only for testing - remove in production!
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    """Reset password using reset token.

    Args:
        request: Reset password request with token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException: 400 if token is invalid, expired, or already used
    """
    # Fetch reset token
    result = await db.execute(
        select(PasswordResetToken).where(PasswordResetToken.token == request.token)
    )
    reset_token = result.scalars().first()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Check if token is valid
    if not reset_token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Fetch user
    result = await db.execute(
        select(User).where(User.user_id == reset_token.user_id)
    )
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Update password
    user.hashed_password = hash_password(request.new_password)

    # Mark token as used
    from datetime import datetime
    reset_token.used = True
    reset_token.used_at = datetime.utcnow()

    await db.commit()

    return MessageResponse(message="Password reset successfully")
