from hashlib import new
from unicodedata import name
from fastapi import FastAPI, Depends, Request, Form, status

from starlette.responses import RedirectResponse
from starlette.templating import Jinja2Templates

from sqlalchemy.orm import Session

import random

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
    view = db.query(models.Views).filter(models.Views.userId == user_id).all()
    favs = db.query(models.Favorites).filter(models.Favorites.userId == user_id).all()
    rec = gerarRec(movies, view, favs, 10)
    catalogo = gerarCatalogo(movies, view, favs)
    return templates.TemplateResponse("filmes.html", {"request": request, "user_id": user_id, "movie_list": catalogo, "rec_list": rec})

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
    relen = db.query(models.Favorites).filter(models.Favorites.userId == user_id, models.Favorites.movieId == movie_id).first()
    try:
        if(not relen.favorite):
            setattr(relen, "favorite", True)
        else:
            setattr(relen, "favorite", False)
        db.add(relen)
    except:
        new_r = models.Favorites(userId=user_id, movieId=movie_id, favorite=True)
        db.add(new_r)
    db.commit()
    url="/catalogo/"+str(user_id)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/assistir/{user_id}/{movie_id}")
def movieView(request: Request, user_id: int, movie_id: int, db: Session = Depends(get_db)):
    new_r = models.Views(userId=user_id, movieId=movie_id, view="Assistiu")
    db.add(new_r)
    db.commit()
    url="/catalogo/"+str(user_id)
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)

@app.get("/assistirmetade/{user_id}/{movie_id}")
def movieViewHalf(request: Request, user_id: int, movie_id: int, db: Session = Depends(get_db)):
    relen = db.query(models.Views).filter(models.Views.userId == user_id, models.Views.movieId == movie_id).first()
    try:
        setattr(relen, "view", "Metade")
        db.add(relen)
    except:
        new_r = models.Views(userId=user_id, movieId=movie_id, view="Metade")
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

def gerarRec(movies, views, favs, qr):
    # Pontuacao
    notas = {
        "Favorito" : 7,
        "Assistiu" : 4,
        "Metade" : 1
    }

    rec = []
    tags = {}

    for v in views: # Loop para cada linha de view
        for m in movies: # loop para cada filme
            if( m.id == v.movieId): # se a view for referente ao movie
                g = m.tags.split(",") # Separa as tags do filme
                for x in range(0, len(g)): # Repete para cada tag do time
                    t = g[x].strip()
                    if t in tags: # Se a tag ja existe
                        tags[t] = tags[t] + notas[v.view] # pega o valor antigo e add
                    else: # senao cria um novo no dic
                        tags[t] = notas[v.view]

    for f in favs:
        for m in movies:
            if( m.id == f.movieId):
                g = m.tags.split(",")
                for x in range(0, len(g)):
                    t = g[x].strip()
                    if t in tags:
                        if f.favorite : tags[t] = tags[t] + notas["Favorito"]
                    else:
                        if f.favorite : tags[t] = notas["Favorito"]

    # Ranquear os filmes
    filmes = {}
    for m in movies:
        filmes[m.id] = 0;
        g = m.tags.split(",")
        for x in range(0, len(g)):
            t = g[x].strip()
            if t in tags : filmes[m.id] = filmes[m.id] + tags[t]

    for v in views:
        if v.movieId in filmes : 
            del filmes[v.movieId]

    # rank = dict(sorted(filmes.items(), key=lambda item: item[1],reverse=True)) 
    rank = dict(sorted(filmes.items(), key=lambda item: item[1], reverse=True))
    
    c = 0;
    for x in rank:
        for m in movies:
            if m.id == x :
                m.nota = rank[x];
                rec.append(m)
                c += 1
            if c > qr:
                break;

    print(tags)

    return rec

def gerarCatalogo(movies, views, favs):
    for m in movies:
        m.assistiu = False
        m.metade = False
        m.favorito = False
        for v in views:
            if m.id == v.movieId:
                if v.view == "Assistiu" : m.assistiu = True
                if v.view == "Metade" : m.metade = True
        for f in favs:
            if m.id == f.movieId:
                if f.favorite : m.favorito = True
    return movies