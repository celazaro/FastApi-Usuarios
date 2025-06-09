from sqlmodel import SQLModel, create_engine, Session 
import os

# Nombre del archivo de base de datos SQLite
sqlite_file_name = "db.sqlite3"
# Obtener la ruta absoluta del directorio del proyecto
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# Crear la ruta completa al archivo de la base de datos
sqlite_url = f"sqlite:///{os.path.join(base_dir, sqlite_file_name)}"

# Requerido por SQLite para evitar errores en aplicaciones asincrónicas
connect_args = {"check_same_thread": False}

# Crear el engine
engine = create_engine(sqlite_url, connect_args=connect_args, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# Dependencia para obtener la sesión
def get_session():
    with Session(engine) as session:
        yield session