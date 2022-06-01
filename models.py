from enum import unique
from sqlalchemy import Boolean, Column, Integer, String

from database import Base

class User(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, unique=True)
    password = Column(String)
    role = Column(String)

class Movie(Base):
    __tablename__ = "Movies"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    tags = Column(String)
    genre = Column(String)

class Views(Base):
    __tablename__ = "Views"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer)
    movieId = Column(Integer)
    view = Column(String)

class Favorites(Base):
    __tablename__ = "Favorites"
    id = Column(Integer, primary_key=True, index=True)
    userId = Column(Integer)
    movieId = Column(Integer)
    favorite = Column(Boolean) 

# OLD
class Todo(Base):
    __tablename__ = "todos"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    complete = Column(Boolean, default=False)