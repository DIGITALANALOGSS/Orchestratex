from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from orchestratex.config import get_settings
from orchestratex.models.auth import User
from orchestratex.schemas.auth import UserCreate, UserUpdate, TokenData
from orchestratex.database import get_db

settings = get_settings()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    def get_current_user(self, token: str) -> Optional[User]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
        except JWTError:
            return None
        
        user = self.db.query(User).filter(User.username == token_data.username).first()
        return user

    def create_user(self, user_data: UserCreate) -> User:
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=self.get_password_hash(user_data.password)
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_user(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[User]:
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if db_user:
            for key, value in user_data.model_dump(exclude_unset=True).items():
                if key == "password":
                    setattr(db_user, "hashed_password", self.get_password_hash(value))
                else:
                    setattr(db_user, key, value)
            self.db.commit()
            self.db.refresh(db_user)
        return db_user

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user(username)
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        return user

    def create_token(self, user: User) -> dict:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.create_access_token(
            data={"sub": user.username},
            expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_at": datetime.utcnow() + access_token_expires
        }
