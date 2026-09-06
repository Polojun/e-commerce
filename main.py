from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from database import get_connection
from pydantic import BaseModel #Entrada y validacion de datos

app =FastAPI(title = "API tienda")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") #Config del encriptador de passwords

#Esquema Pydantic: Estructura esperada en el cuerpo del JSON
class UserRegister(BaseModel):
    name: str
    password_hash: str

#Endpoint POST para registrar usuarios
@app.post("/register")
def register_user(user: UserRegister):
    conn = get_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error en conexión a database")

    hashed_password = pwd_context.hash(user.password_hash) #Encripta contraseña recibida antes de guardarla

    try:
        with conn.cursor() as cursor:
            #Consulta SQL con %s para prevenir inyecciones SQL
            cursor.execute(
                """
                INSERT INTO users (name, password_hash)
                VALUES (%s, %s) RETURNING id, name, creation_date
                """,
                (user.name, hashed_password)
            )

            new_user = cursor.fetchone() #Obtiene el usuario recién creado
            conn.commit() #Confirma la transacción en PostgreSQL
        return{
            "mensaje": "Usuario registrado exitosamente",
            "usuario": {
            "id": new_user[0],
            "name": new_user[1],
            "creation_date": new_user[2]
        }
    }
    except Exception as e:
        conn.rollback() #Cancela cambios en caso de fallo
        if "duplicate key value" in str(e):
            raise HTTPException(status_code=400, detail="El nombre de usuario ya existe")

        raise HTTPException(status_code=500, detail=f"Error al registrar usuario: {e}")
    finally:
        conn.close() #Cierra la conexión a la base de datos



    

    
