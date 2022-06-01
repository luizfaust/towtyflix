from hashlib import new
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
def register(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("cadastro.html", {"request": request})

@app.get("/catalogo/{user_id}")
def movieCatalog(request: Request, user_id: int, db: Session = Depends(get_db)):
    movies = db.query(models.Movie).all()
    relen = db.query(models.Relationship).filter(models.Relationship.userId == user_id).all()
    #gerar
    return templates.TemplateResponse("filmes.html", {"request": request, "user_id": user_id, "movie_list": movies, "relen_list": relen})

@app.post("/login")
def logar(request: Request, user: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.user == user, models.User.password == password).first()
    print(hash(password))
    try:
        url = "catalogo/" + str(user.id)
    except:
        url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.post("/addUser")
def add(request: Request, user: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    new_User = models.User(user=user, password=password, role="User")
    db.add(new_User)
    db.commit()
    url = "catalogo/" + str(new_User.id)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/favoritar/{user_id}/{movie_id}")
def movieFav(request: Request, user_id: int, movie_id: int, db: Session = Depends(get_db)):
    relen = db.query(models.Relationship).filter(models.Relationship.userId == user_id, models.Relationship.movieId == movie_id).first()
    try:
        if(relen.preference == None):
            setattr(relen, "preference", "Favorito")
        else:
            setattr(relen, "preference", None)
        db.add(relen)
    except:
        new_r = models.Relationship(userId=user_id, movieId=movie_id, preference="Favorito")
        db.add(new_r)
    db.commit()
    url="/catalogo/"+str(user_id)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/assistir/{user_id}/{movie_id}")
def movieView(request: Request, user_id: int, movie_id: int, db: Session = Depends(get_db)):
    relen = db.query(models.Relationship).filter(models.Relationship.userId == user_id, models.Relationship.movieId == movie_id).first()
    try:
        setattr(relen, "view", "Assistiu")
        db.add(relen)
    except:
        new_r = models.Relationship(userId=user_id, movieId=movie_id, view="Assistiu")
        db.add(new_r)
    db.commit()
    url="/catalogo/"+str(user_id)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/assistirmetade/{user_id}/{movie_id}")
def movieViewHalf(request: Request, user_id: int, movie_id: int, db: Session = Depends(get_db)):
    relen = db.query(models.Relationship).filter(models.Relationship.userId == user_id, models.Relationship.movieId == movie_id).first()
    try:
        setattr(relen, "view", "Metade")
        db.add(relen)
    except:
        new_r = models.Relationship(userId=user_id, movieId=movie_id, view="Metade")
        db.add(new_r)
    db.commit()
    url="/catalogo/"+str(user_id)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/cadastroFilme")
def home(request: Request, db: Session = Depends(get_db)):
    return templates.TemplateResponse("cadastroFilme.html", {"request": request})

@app.post("/addMovie")
def add(request: Request, name: str = Form(...), tags: str = Form(...), genre: str = Form(...),  db: Session = Depends(get_db)):
    new_Movie = models.Movie(name=name, genre=genre, tags=tags)
    db.add(new_Movie)
    db.commit()
    url = "/cadastroFilme"
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

def gerarRec(relen):
    Rec = []
    if(relen == None):
        for x in range(1, 10):
            print(x)
    
    print(relen)