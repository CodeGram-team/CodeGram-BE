from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from db.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4())
    email = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text('now()'))
    
    social_accounts = relationship("SocialAccount", back_populates="user", cascade="all, delete-orphan")

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    provider = Column(String, nullable=False)
    provider_user_id = Column(String, nullable=False)
    
    user = relationship("User", back_populates="social_accounts")

    __table_args__ = (
        UniqueConstraint('provider_user_id', name='uq_social_accounts_provider_user_id', postgresql_nulls_not_distinct=False),
    )