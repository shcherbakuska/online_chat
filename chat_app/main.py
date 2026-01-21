from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from typing import Dict, List
import jwt
from jwt.exceptions import InvalidTokenError
from database.database import get_db, User
from sqlalchemy.orm import Session
import logging

# Конфигурация JWT
SECRET_KEY = "try_to_catch_me"
ALGORITHM = "HS256"

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI()

# Управление подключениями
class Room_Manager:
    def __init__(self):
        self.rooms: Dict[str, List[WebSocket]] = {}  

    async def connect(self, websocket: WebSocket, room_name: str):
        if room_name not in self.rooms:
            self.rooms[room_name] = []
        self.rooms[room_name].append(websocket)
        await websocket.accept()
        logger.info(f"Подключение пользователя к комнате: {room_name}, всего подключений: {len(self.rooms[room_name])}")

    def disconnect(self, websocket: WebSocket, room_name: str):
        if room_name in self.rooms:
            self.rooms[room_name].remove(websocket)
            logger.info(f"Отключение пользователя от комнаты: {room_name}, оставшиеся подключения: {len(self.rooms.get(room_name, []))}")
            if not self.rooms[room_name]:
                del self.rooms[room_name]
                logger.info(f"Комната {room_name} теперь пуста и удалена.")

    async def broadcast(self, message: str, room_name: str):
        logger.info(f"Рассылка сообщения в комнате {room_name}: {message}")
        for websocket in self.rooms.get(room_name, []):
            await websocket.send_text(message)

manager = Room_Manager()

# Проверка JWT токена
def validate_jwt(token: str, db: Session) -> str:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise credentials_exception

        user = db.query(User).filter(User.email == user_email).first()
        if not user:
            raise credentials_exception

        return user_email
    except InvalidTokenError as e:
        logger.warning(f"Ошибка валидации токена: {str(e)}")
        raise credentials_exception

# Подключение к чат-комнате
@app.websocket("/ws/{room_name}")
async def websocket_endpoint(websocket: WebSocket, room_name: str, token: str = Query(...), db: Session = Depends(get_db)):
    try:
        user_email = validate_jwt(token, db)
        user = db.query(User).filter(User.email == user_email).first()
        username=user.username
        logger.info(f"Пользователь {username} пытается подключиться к комнате {room_name}.")
        await manager.connect(websocket, room_name)
        await manager.broadcast(f"Пользователь {username} подключился к диалогу", room_name)

        while True:
            try:
                data = await websocket.receive_text()
                logger.info(f"Сообщение от пользователя {username} в комнате {room_name}: {data}")
                await manager.broadcast(f"{username}: {data}", room_name)
            except WebSocketDisconnect:
                manager.disconnect(websocket, room_name)
                logger.info(f"Пользователь {username} отключился от комнаты {room_name}.")
                await manager.broadcast(f"Пользователь {username} отключился", room_name)
                break
    except Exception as e:
        logger.error(f"Ошибка WebSocket: {str(e)}")
        await websocket.close()
