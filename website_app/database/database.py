from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base



DATABASE_URL = "postgresql://anya:Qq123456@db:5432/basic_db"
# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Base class for models
Base = declarative_base()

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency to get the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Using models
class User(Base):
    __tablename__ = "users"
    
    email = Column(String,primary_key=True, unique=True, index=True, nullable=False)
    username = Column(String, index=True)
    hashed_password = Column(String, nullable=False)
    # One-to-Many relationship: User can have multiple posts
    chat_rooms = relationship("Chat", back_populates="owner")

 
class Chat(Base):
    __tablename__ = "chats"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    owner_id = Column(String, ForeignKey("users.email"), nullable=False)
    owner = relationship("User", back_populates="chat_rooms")

