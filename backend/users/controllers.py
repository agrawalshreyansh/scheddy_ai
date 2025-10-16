from sqlalchemy.orm import Session
from users.models import User
from users.schemas import UserCreate, UserUpdate
from passlib.context import CryptContext
from typing import Optional, List
from uuid import UUID

# Password hashing context with truncate_error disabled
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    password = password.encode("utf-8")[:72].decode("utf-8")
    print(password)
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """Get a user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get a user by username"""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get a list of users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    # hashed_password = get_password_hash(user.password)
    print(user.password)
    hashed_password = user.password
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user



def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    """Update a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    
    # Hash password if it's being updated
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username and password"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    # Plain password comparison since we're storing plain passwords
    if password != user.hashed_password:
        return None
    return user


def create_access_token(data: dict) -> str:
    """Create a JWT access token"""
    from datetime import datetime, timedelta
    from jose import jwt
    from config import AuthConfig
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, AuthConfig.SECRET_KEY, algorithm=AuthConfig.ALGORITHM)
    return encoded_jwt


def get_current_user(db: Session, token: str) -> Optional[User]:
    """Get current user from JWT token"""
    from jose import JWTError, jwt
    from config import AuthConfig
    
    try:
        payload = jwt.decode(token, AuthConfig.SECRET_KEY, algorithms=[AuthConfig.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = get_user_by_username(db, username=username)
    return user
