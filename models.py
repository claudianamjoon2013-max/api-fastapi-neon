from pydantic import BaseModel

class CategoriaCreate(BaseModel):
    nombre: str

class ProductoCreate(BaseModel):
    nombre: str
    precio: float
    stock: int = 0
    categoria_id: int

class ProductoUpdate(BaseModel):
    nombre: str
    precio: float
    stock: int
    categoria_id: int

class LoginRequest(BaseModel):
    usuario: str
    password: str

class Empleado(BaseModel):
    documento: int
    nombre: str
    cargo: str
    salario: float

class EmpleadoUpdate(BaseModel):
    nombre: str
    cargo: str
    salario: float