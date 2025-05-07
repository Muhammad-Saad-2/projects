from sqlmodel import Column, Integer, String, DateTime, ForeignKey, Boolean, Relationship, func
from ..utils.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    bio = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    followers = Relationship("Follow", foreign_keys="Follow.followed_id", back_populates="followed")
    following = Relationship("Follow", foreign_keys="Follow.follower_id", back_populates="follower")

class Follow(Base):
    __tablename__ = "follows"
    
    id = Column(Integer, primary_key=True, index=True)
    follower_id = Column(Integer, ForeignKey("users.id"))
    followed_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    follower = Relationship("User", foreign_keys=[follower_id], back_populates="following")
    followed = Relationship("User", foreign_keys=[followed_id], back_populates="followers") 