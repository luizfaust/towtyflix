from sqlalchemy import Boolean, Column, Integer, String

from database import Base

class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String)
    password = Column(String)
    role = Column(String)

class Movie(Base):
    __tablename__ = "Movies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    tags = Column(String)
    genre = Column(String)

class Relationship(Base):
    __tablename__ = "Relationships"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer)
    movieId = Column(Integer)
    view = Column(String)
    preference = Column(String) 

# OLD
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    complete = Column(Boolean, default=False)