from fastapi import FastAPI, Request, Depends, Query, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from auth.auth import existing_token, create_access_token, get_password_hash, verify_password, get_current_user
from database.database import Base, engine, get_db, User, Chat
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import os

Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

app.add_middleware(SessionMiddleware, secret_key="feel_happy")

def delete_room(db: Session, room_name: str, user_email: str):
    room = db.query(Chat).filter(Chat.name == room_name, Chat.owner_id == user_email).first()
    if room:
        db.delete(room)
        db.commit()

def add_room(db: Session, room_name: str, user_email: int):
    created_room = Chat(name=room_name, owner_id=user_email)
    db.add(created_room)
    db.commit()
    db.refresh(created_room)
    return created_room

# Стартовая страница
@app.get("/")
async def start_page(request: Request):
    return templates.TemplateResponse("start.html", {"request": request})

# Страница регистарции
@app.get("/register", response_class=HTMLResponse)
async def get_register(request: Request, success: str | None = Query(default=None), error: str | None = Query(default=None)):
    return templates.TemplateResponse("register.html", {"request": request, "success": success, "error": error})

@app.post("/register")
async def register(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == email).first()
    if db_user:
        return RedirectResponse(f"/register?error=Пользователь с такими данными уже существует! ", status_code=302)
    db_user = User(email=email, username=username, hashed_password=get_password_hash(password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(data={"sub": db_user.email})
    request.session["access_token"] = access_token
    return RedirectResponse("/user", status_code=302)

# Страница аутентификации
@app.get("/login", response_class=HTMLResponse)
async def get_login(request: Request, error: str | None = Query(default=None)):
    access_token = request.session.get("access_token")
    if access_token and not existing_token(access_token):
        return RedirectResponse("/user", status_code=302)
    else:
        return templates.TemplateResponse("login.html", {"request": request, "error": error})


@app.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        return RedirectResponse(f"/login?error=Неверная почта или пароль! ", status_code=302)
    
    access_token = create_access_token(data={"sub": user.email})
    request.session["access_token"] = access_token
    return RedirectResponse("/user", status_code=302)

@app.get("/logout", response_class=RedirectResponse)
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/login", status_code=302)

# Личный кабинет пользователя
@app.get("/user", response_class=HTMLResponse)
async def user(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if "access_token" not in request.session:
        return RedirectResponse("/login", status_code=302)

    user_email = current_user.email
    user = db.query(User).filter(User.email == user_email).first()
    user_rooms = db.query(Chat).filter(Chat.owner_id == user_email).all()
    error_message = request.query_params.get("error", None)

    return templates.TemplateResponse("user.html", {"request": request, "rooms": user_rooms, "user_email": user_email, "username": user.username, "error": error_message})

# Создание новой чат-комнаты
@app.post("/user/rooms", response_class=RedirectResponse)
async def create_room(request: Request, room_name: str = Form(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if "access_token" not in request.session:
        return RedirectResponse("/login", status_code=302)
    
    user_email = current_user.email

    room_naming = db.query(Chat).filter(Chat.name == room_name).first()
    if room_naming:
        return RedirectResponse("/user?error=Комната c таким названием уже существует!", status_code=302)

    if len(room_name) < 6:
        return RedirectResponse("/user?error=Название чата должно содержать 6 символов!", status_code=302)

    add_room(db, room_name, user_email)
    
    return RedirectResponse("/user", status_code=302)

# Удаление созданной чат-комнаты
@app.delete("/user/rooms/delete/{room_name}", response_class=RedirectResponse)
async def delete_room_route(request: Request, room_name: str, db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)):
    if "access_token" not in request.session:
        return RedirectResponse("/login", status_code=302)

    user_email = current_user.email
    delete_room(db, room_name, user_email)
    return RedirectResponse("/user", status_code=302)

# Поиск чат-комнаты
@app.get("/user/search", response_class=HTMLResponse)
async def search_rooms(request: Request):
    if "access_token" not in request.session:
        return RedirectResponse("/login", status_code=302)

    return templates.TemplateResponse("search.html", {"request": request, "rooms": []})

# Результат поиска комнаты
@app.get("/user/search/results", response_class=HTMLResponse, )
async def search_rooms_results(request: Request, query: str, db: Session = Depends(get_db)):
    if len(query) < 6:
        return templates.TemplateResponse("search.html", {"request": request, "error": "Запрос должен содержать как минимум 6 символов!", "rooms": []})

    search_results = db.query(Chat).filter(Chat.name.contains(query)).all()
    return templates.TemplateResponse("search.html", {"request": request, "rooms": search_results, "search_query": query})

#GET-запрос для получения токена и названия комнаты
@app.get("/api/chat_data/{room_name}")
async def get_chat_data(room_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    user_email = current_user.email
    room = db.query(Chat).filter(Chat.name == room_name).first()
    if not room:
        return {"error": "Чат-комната не найдена!"}

    token = create_access_token(data={"sub": user_email})
    return {"room_name": room_name, "token": token}

# Чат-комната 
@app.get("/chat/{room_name}", response_class=HTMLResponse)
async def get_chat(request: Request, room_name: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if "access_token" not in request.session:
        return RedirectResponse("/login", status_code=302)

    room = db.query(Chat).filter(Chat.name == room_name).first()
    if not room:
        return HTMLResponse(content="Чат-комната не найдена!", status_code=404)

    return templates.TemplateResponse("chat.html", {"request": request})
