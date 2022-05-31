from fastapi import FastAPI, Depends, Request, Form, status

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session

import models
from database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    todos = db.query(models.Todo).all()
    users = db.query(models.User).all()
    return templates.TemplateResponse("base.html", {"request": request, "todo_list": todos, "user_list": users})


@app.post("/addUser")
def add(request: Request, user: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    new_User = models.User(user=user, password=hash(password), role="User")
    db.add(new_User)
    db.commit()
    user = db.query(models.User).filter(models.User.user == user).first()
    id = int(user.id)
    print(type(id))
    return RedirectResponse(url="/lista/{id}", status_code=status.HTTP_303_SEE_OTHER)


@app.get("/lista/{user_id}")
def home(request: Request, user_id: int, db: Session = Depends(get_db)):
    return templates.TemplateResponse("lista.html", {"request": request, "user_id": user_id})


@app.get("/update/{todo_id}")
def update(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.complete = not todo.complete
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)


@app.get("/delete/{todo_id}")
def delete(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()

    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_302_FOUND)