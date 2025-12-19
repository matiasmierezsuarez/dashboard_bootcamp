"""
Configuración de conexión a la base de datos Neon PostgreSQL
"""

DATABASE_URL = "postgresql://neondb_owner:npg_SJdoFw30tYsb@ep-empty-butterfly-ahn1ymen-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

# Configuración de pool de conexiones
DB_CONFIG = {
    "pool_size": 5,
    "max_overflow": 10,
    "pool_timeout": 30,
    "pool_recycle": 3600,
}