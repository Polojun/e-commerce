import psycopg #necesario para conectar postgresql

#Establecer parametros de conexion a la base de datos
dbname = "tienda_db"
user = "postgres" #default user
password = "Golden3010" 
host = "localhost" #direccion ip de postgres
port = "5432"

#conectar database
def get_connection():
    try:
        conn = psycopg.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        return conn
    except Exception as e:
        print("Error al conectar a la base de datos:", e)
        return None              


def try_connection():
    conn = get_connection()
    if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT *FROM users")
                usuario = cursor.fetchone()
                
                print("--- CONEXIÓN EXITOSA ---")
                print(f"Usuario encontrado: {usuario}")
                
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"Error al hacer la consulta: {e}")
    else:
        print("No se pudo conectar a la base de datos.")

#try_connection()
#comentamos para que no se ejecute
