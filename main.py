from fastapi import FastAPI, HTTPException, status
from psycopg2.extras import RealDictCursor
from psycopg2.errors import ForeignKeyViolation, UniqueViolation

from database import get_connection, crear_tablas
from models import (
    CategoriaCreate, ProductoCreate, ProductoUpdate,
    LoginRequest, Empleado, EmpleadoUpdate
)

app = FastAPI()

crear_tablas()

@app.get("/")
def inicio():
    return {"mensaje": "API FUNCIONANDO CORRECTAMENTE"}


# CATEGORÍAS
@app.post("/categorias", status_code=status.HTTP_201_CREATED)
def crear_categoria(categoria: CategoriaCreate):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO categorias (nombre) VALUES (%s) RETURNING *;",
            (categoria.nombre,)
        )
        nueva_cat = cur.fetchone()
        conn.commit()
        return nueva_cat
    except UniqueViolation:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="La categoría con ese nombre ya existe."
        )
    finally:
        cur.close()
        conn.close()

@app.get("/categorias")
def listar_categorias():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categorias ORDER BY id ASC;")
    categorias = cur.fetchall()
    cur.close()
    conn.close()
    return categorias

@app.get("/categorias/{id}")
def obtener_categoria(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM categorias WHERE id = %s;", (id,))
    categoria = cur.fetchone()
    cur.close()
    conn.close()
    
    if not categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    return categoria

@app.delete("/categorias/{id}")
def eliminar_categoria(id: int):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT * FROM categorias WHERE id = %s;", (id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")
    
    try:
        cur.execute("DELETE FROM categorias WHERE id = %s;", (id,))
        conn.commit()
        return {"mensaje": f"Categoría con id {id} eliminada correctamente."}
    except ForeignKeyViolation:
        conn.rollback()
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar la categoría porque tiene productos asociados."
        )
    finally:
        cur.close()
        conn.close()


# PRODUCTOS
@app.post("/productos", status_code=status.HTTP_201_CREATED)
def crear_producto(producto: ProductoCreate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM categorias WHERE id = %s;", (producto.categoria_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="La categoría especificada no existe.")

    cur.execute(
        """
        INSERT INTO productos (nombre, precio, stock, categoria_id)
        VALUES (%s, %s, %s, %s) RETURNING *;
        """,
        (producto.nombre, producto.precio, producto.stock, producto.categoria_id)
    )
    nuevo_producto = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return nuevo_producto

@app.get("/productos")
def listar_productos():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos ORDER BY id ASC;")
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return productos

@app.get("/productos/stock-bajo/{minimo}")
def productos_stock_bajo(minimo: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE stock <= %s ORDER BY stock ASC;", (minimo,))
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return productos




@app.get("/productos/{id}")
def obtener_producto(id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM productos WHERE id = %s;", (id,))
    producto = cur.fetchone()
    cur.close()
    conn.close()

    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado.")
    return producto

@app.get("/categorias/{id}/productos")
def listar_productos_por_categoria(id: int):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("SELECT id FROM categorias WHERE id = %s;", (id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Categoría no encontrada.")

    cur.execute("SELECT * FROM productos WHERE categoria_id = %s;", (id,))
    productos = cur.fetchall()
    cur.close()
    conn.close()
    return productos

@app.put("/productos/{id}")
def actualizar_producto(id: int, producto: ProductoUpdate):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM productos WHERE id = %s;", (id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    cur.execute("SELECT id FROM categorias WHERE id = %s;", (producto.categoria_id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="La nueva categoría especificada no existe.")

    cur.execute(
        """
        UPDATE productos
        SET nombre = %s, precio = %s, stock = %s, categoria_id = %s
        WHERE id = %s RETURNING *;
        """,
        (producto.nombre, producto.precio, producto.stock, producto.categoria_id, id)
    )
    producto_actualizado = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return producto_actualizado

@app.delete("/productos/{id}")
def eliminar_producto(id: int):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM productos WHERE id = %s;", (id,))
    if not cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Producto no encontrado.")

    cur.execute("DELETE FROM productos WHERE id = %s;", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": f"Producto con id {id} eliminado correctamente."}






# USUARIOS / LOGIN
@app.post("/login")
def validar_usuario(datos: LoginRequest):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        "SELECT * FROM usuarios WHERE usuario = %s AND password = %s;",
        (datos.usuario, datos.password)
    )
    usuario_encontrado = cur.fetchone()
    cur.close()
    conn.close()

    if usuario_encontrado:
        return {"mensaje": "existe"}

    return {"mensaje": "no existe"}

@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: LoginRequest):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO usuarios (usuario, password) VALUES (%s, %s);",
            (datos.usuario, datos.password)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="El usuario ya existe o hubo un error en los datos")
    
    cur.close()
    conn.close()
    return {"mensaje": "Usuario registrado exitosamente"}


# EMPLEADOS
@app.get("/empleados")
def listar_empleados():
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM empleados;")
    empleados = cur.fetchall()
    cur.close()
    conn.close()
    return empleados

@app.get("/empleados/{documento}")
def obtener_empleado(documento: int):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM empleados WHERE documento = %s;", (documento,))
    empleado = cur.fetchone()
    cur.close()
    conn.close()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@app.post("/empleados", status_code=status.HTTP_201_CREATED)
def crear_empleado(emp: Empleado):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO empleados (documento, nombre, cargo, salario) VALUES (%s, %s, %s, %s);",
            (emp.documento, emp.nombre, emp.cargo, emp.salario)
        )
        conn.commit()
    except Exception:
        conn.rollback()
        cur.close()
        conn.close()
        raise HTTPException(status_code=400, detail="El documento ya existe o hubo un error en los datos")
    cur.close()
    conn.close()
    return {"mensaje": "Empleado registrado exitosamente"}

@app.put("/empleados/{documento}")
def actualizar_empleado(documento: int, emp: EmpleadoUpdate):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE empleados SET nombre = %s, cargo = %s, salario = %s WHERE documento = %s;",
        (emp.nombre, emp.cargo, emp.salario, documento)
    )
    filas_afectadas = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return {"mensaje": "Empleado actualizado exitosamente"}

@app.delete("/empleados/{documento}")
def eliminar_empleado(documento: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM empleados WHERE documento = %s;", (documento,))
    filas_afectadas = cur.rowcount
    conn.commit()
    cur.close()
    conn.close()
    if filas_afectadas == 0:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return {"mensaje": "Empleado eliminado exitosamente"}