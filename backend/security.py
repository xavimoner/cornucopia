# backend/security.py
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt # Assegura't que 'jose' estigui al requirements.txt
from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
from typing import Optional, Dict


import db 
import models

load_dotenv()

# Configuració de Passlib per al hashing de contrasenyes
from passlib.context import CryptContext 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuració JWT (llegida del .env)
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
   

    print("ADVERTENCIA CRITICA: SECRET_KEY no está configurada en las variables de entorno.")



def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: Dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    if not SECRET_KEY: # Comprovació abans d'usar
        raise ValueError("No se puede crear el token JWT: SECRET_KEY no está definida.")
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str) -> Optional[Dict]:
    try:
        if not SECRET_KEY: # Comprovació abans d'usar
            print("ERROR: No se puede decodificar el token JWT: SECRET_KEY no está definida.")
            return None
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e: 
        print(f"WARN: Error de JWT al decodificar token: {e}")
        return None

# URL on  client anirà a obtenir  token (endpoint /token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class UsuariNoAutenticatException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se han podido validar las credenciales",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme), 
    db_session: Session = Depends(db.get_db) 
) -> models.Usuari: 
    payload = decode_access_token(token)
    if payload is None:
        print("WARN: Token inválido o expirado (payload es None)")
        raise UsuariNoAutenticatException()
    
    nom_usuari: Optional[str] = payload.get("sub")
    if nom_usuari is None:
        print("WARN: Token no contiene 'sub' (nom_usuari)")
        raise UsuariNoAutenticatException()
    
    usuari = db_session.query(models.Usuari).filter(models.Usuari.nom_usuari == nom_usuari).first()
    if usuari is None:
        print(f"WARN: Usuario '{nom_usuari}' del token no encontrado en la BD")
        raise UsuariNoAutenticatException()
    return usuari


async def get_current_active_user(
    current_user: models.Usuari = Depends(get_current_user)
) -> models.Usuari:
    if not current_user.actiu:
        print(f"WARN: Intento de acceso por usuario inactivo: {current_user.nom_usuari}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo")
    print(f"INFO: Usuario activo autenticado: {current_user.nom_usuari}") 
    return current_user

# Dependència per a usuaris amb rol d'administrador
async def get_current_admin_user(
    current_user: models.Usuari = Depends(get_current_active_user)
) -> models.Usuari:
    if current_user.rol != "administrador":
        print(f"WARN: Acceso no autorizado a ruta de admin por usuario: {current_user.nom_usuari} (rol: {current_user.rol})")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="La operación requiere privilegios de administrador",
        )
    return current_user