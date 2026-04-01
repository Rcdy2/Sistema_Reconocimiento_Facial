import pyodbc
import logging

# Configurar logging para ver el progreso en consola
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db_connection():
    # Solo intentaremos con el Driver 17 para evitar esperas largas
    driver = '{ODBC Driver 17 for SQL Server}'
    server = 'localhost' # Usa localhost en lugar de punto para mayor compatibilidad
    database = 'UTP_SECURITYFACIAL'

    try:
        # Agregamos un timeout de conexión de 2 segundos para que no se cuelgue el programa
        conn_str = (
            f"DRIVER={driver};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
            "Connection Timeout=2;"
        )
        logger.info(f"Intentando conectar a {server}...")
        conn = pyodbc.connect(conn_str)
        return conn
    except Exception as e:
        logger.error(f"Error de conexión: {e}")
        # Si falla el 17, intenta el 18 rápido
        try:
            conn_str = conn_str.replace("Driver 17", "Driver 18")
            return pyodbc.connect(conn_str)
        except:
            return None