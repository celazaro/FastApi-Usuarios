from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from app.db.database import create_db_and_tables
from app.api import users, auth, private, profiles     
# Importamos el router de usuarios (lo crearemos en breve)


app = FastAPI()

# Configurar CORS si es necesario
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Montar el directorio media para servir archivos estáticos
app.mount("/media", StaticFiles(directory="media"), name="media")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Asegurarse de que existe el directorio media
    Path("media").mkdir(exist_ok=True)


# Incluir rutas de usuarios
app.include_router(users.router, prefix="/users", tags=["users"])

app.include_router(auth.router)  # <- agregamos auth.router

# Incluir endpoints protegidos, como /me
app.include_router(private.router, tags=["private"])

app.include_router(profiles.router, prefix="/profiles", tags=["profiles"])  # Nueva línea


