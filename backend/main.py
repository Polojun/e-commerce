from fastapi import FastAPI, HTTPException
from passlib.context import CryptContext
from database import get_connection
from pydantic import BaseModel #Entrada y validacion de datos
from fastapi.middleware.cors import CORSMiddleware

app =FastAPI(title = "API tienda")

origins = [ #de donde se permiten peticiones a la API
    "http://localhost:4200",
    "http://localhost:3000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], #Metodos HTTP permitidos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"]
)

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


#Esquema Pydantic para login
class UserLogin(BaseModel):
    name: str
    password_hash: str

# Endpoint POST para login de usuarios
@app.post("/login")
def login_user(user: UserLogin):
    conn = get_connection()
    if conn is None:
        raise HTTPException(status_code=500, detail="Error en conexión a database")

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, name, password_hash FROM users WHERE name = %s;", (user.name,)
            )
            found_user = cursor.fetchone() #Obtiene una tupla con los campos del usuario de postgresql

        if not found_user:
            raise HTTPException(status_code=401, detail="Credenciales inválidas")
        user_id, username, stored_password_hash = found_user

        if not pwd_context.verify(user.password_hash, stored_password_hash): #Compara la contraseña ingresada con la almacenada
            raise HTTPException(status_code=401, detail="Credenciales inválidas")

        return {
            "mensaje": "Login exitoso",
            "usuario": {
                "id": user_id,
                "name": username
            }
        }
    except HTTPException as http_ex:
        raise http_ex
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al iniciar sesión: {e}")
    finally:
        conn.close() #Cierra la conexión a la base de datos
        


    

    
