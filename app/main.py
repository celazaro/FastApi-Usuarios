from fastapi import FastAPI
from app.db.database import create_db_and_tables
from app.api import users, auth, private, profiles     
# Importamos el router de usuarios (lo crearemos en breve)


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


# Incluir rutas de usuarios
app.include_router(users.router, prefix="/users", tags=["users"])

app.include_router(auth.router)  # <- agregamos auth.router

# Incluir endpoints protegidos, como /me
app.include_router(private.router, tags=["private"])

app.include_router(profiles.router, prefix="/profiles", tags=["profiles"])  # Nueva línea


