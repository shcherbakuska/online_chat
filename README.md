«Разработка Веб сервиса»

Структура:

|        Имя файла               |                 Описание                                                                 |
| :----------------------------: | :---------------------------------------------------------------------------------------:|
| docker-compose.yml	         | Файл для запуска всех сервисов через Docker                                              |
|   README.md                    | Документация проекта                                                                     |
| .gitignore	                 | Исключения для Git, чтобы избежать добавления лишних файлов в репозиторий                |
|.dockerignore	                 | Исключения для Docker, чтобы не копировать ненужные файлы в образ                        |
|website/	                     | Микросервис управления пользователями и чат-комнатами                                    |
|website/Dockerfile              | Docker-файл для сборки образа микросервиса website                                       |
|website/main.py                 | Основной файл приложения FastAPI для управления пользователями                           |
|website/requirements.txt	     | Список зависимостей Python для микросервиса website                                      |
|website/__init__.py	         | Инициализационный файл Python для микросервиса                                           |
|website/auth/	                 | Модуль аутентификации                                                                    |
|website/auth/__init__.py	     | Инициализационный файл Python для модуля auth                                            |
|website/auth/auth.py	         | Модуль для работы с аутентификацией через JWT и OAuth2PasswordBearer                     |
|website/database/	             | Логика работы с базой данных                                                             |
|website/database/__init__.py    |	Инициализационный файл Python для модуля database                                       |
|website/database/database.py    |	Модели SQLAlchemy и взаимодействие с базой данных PostgreSQL                            |
|website/templates/	             | Jinja2-шаблоны для фронтенда                                                             |
|website/templates/start.html    | Фронтенд стартовой страницы                                                              |
|website/templates/register.html | Фронтенд страницы регистрации                                                            |
|website/templates/login.html	 | Фронтенд страницы входа                                                                  |
|website/templates/user.html	 | Фронтенд пользовательской страницы с возможностью создания и удаления чатов              |
|website/templates/search.html	 | Фронтенд страницы поиска чатов                                                           | 
|website/templates/chat.html	 | Фронтенд страницы чата с подключением WebSocket                                          |
|chat/	                         | Микросервис WebSocket-чата                                                               |
|chat/Dockerfile	             | Docker-файл для сборки образа микросервиса chat                                          |
|chat/requirements.txt	         | Список зависимостей Python для микросервиса chat                                         |
|chat/__init__.py	             | Инициализационный файл Python для микросервиса chat                                      |
|chat/main.py	                 | Основной файл приложения с логикой управления подключениями WebSocket                    |
|chat/database/	                 | Логика работы с базой данных для микросервиса chat                                       |
|chat/database/__init__.py	     | Инициализационный файл Python для модуля database                                        |
|chat/database/database.py	     | Модели SQLAlchemy и взаимодействие с базой данных PostgreSQL                             |
|db/	                         | Конфигурация базы данных (создается самостоятельно при первом запуске контейнера)        |
|nginx/	                         | Конфигурация веб-сервера Nginx                                                           |
|nginx/nginx.conf	             | Основной конфигурационный файл Nginx                                                     |
|nginx/Dockerfile	             | Docker-файл для сборки образа Nginx                                                      |


Автор: Щерба Анна Андреевна