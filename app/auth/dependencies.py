import logging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.database import SessionLocal
from app.core.config import settings
from app.auth import models

 
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

 
security = HTTPBearer()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_id = int(payload.get("sub"))
        if user_id is None:
            logger.warning("JWT decode failed: 'sub' not found in payload")
            raise credentials_exception
    except JWTError as e:
        logger.warning(f"JWT error: {e}")
        raise credentials_exception

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if user is None:
        logger.warning(f"Authentication failed: User with id '{user_id}' not found")
        raise credentials_exception

    return user


def require_admin(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != models.RoleEnum.admin:
        logger.warning(f"Admin access denied for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def require_user(current_user: models.User = Depends(get_current_user)) -> models.User:
    if current_user.role != models.RoleEnum.user:
        logger.warning(f"User-level access denied for user: {current_user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User access required"
        )
    return current_user