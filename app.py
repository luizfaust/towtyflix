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
    users = db.query(models.User).all()
    return templates.TemplateResponse("base.html", {"request": request, "user_list": users})


@app.get("/cadastro")
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("cadastro.html", {"request": request})

@app.get("/catalogo/{user_id}")
def home(request: Request, user_id: int, db: Session = Depends(get_db)):
    return templates.TemplateResponse("filmes.html", {"request": request, "user_id": user_id})

@app.post("/addUser")
def add(request: Request, user: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    new_User = models.User(user=user, password=hash(password), role="User")
    db.add(new_User)
    print(db)
    db.commit()
    url = "/filmes/" + str(new_User.id)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/cadastroFilme")
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("cadastroFilme.html", {"request": request})

@app.post("/addMovie")
def add(request: Request, name: str = Form("name"), tags: str = Form(...), genre: str = Form(...),  db: Session = Depends(get_db)):
    #new_Movie = models.Movie(name="Titanic", genre="Romance", tags="Romance, Titanic")
    print(name)
    new_Movie = models.Movie(name=name, genre=genre, tags=tags)
    db.add(new_Movie)
    db.commit()
    url = "/cadastroFilme"
    #url = app.url_path_for("home")
    #return RedirectResponse(url=url)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)