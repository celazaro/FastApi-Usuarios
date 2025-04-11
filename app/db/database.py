from sqlmodel import SQLModel, create_engine, Session 

# Nombre del archivo de base de datos SQLite
sqlite_file_name = "db.sqlite3"
sqlite_url = f"sqlite:///{sqlite_file_name}"

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