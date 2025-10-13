"""Permission utilities placeholder."""

from app.models.user import User, UserRole


def require_role(user: User, role: UserRole) -> None:
    if user.role != role:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )