import os

class Config:
    # Configuración para la base de datos PostgreSQL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Ajusta estos valores con tu configuración de pgAdmin:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or "postgresql://postgres@localhost:5432/3tablasSQL"
