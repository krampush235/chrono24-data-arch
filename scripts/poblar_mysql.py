import os
import random
import pymysql
from faker import Faker
from dotenv import load_dotenv
from catalogo import CATALOGO, PAIS_MARCA

load_dotenv()
fake = Faker("es_ES")

conexion = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASS"),
    database=os.getenv("MYSQL_DB"),
)
cursor = conexion.cursor()

# Vaciar las tablas para empezar de cero
cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
for tabla in ["pedidos", "anuncios", "compradores", "vendedores", "marcas"]:
    cursor.execute(f"TRUNCATE TABLE {tabla}")
cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

# Marcas
ids_marca = {}
for nombre in CATALOGO:
    cursor.execute("INSERT INTO marcas (nombre, pais) VALUES (%s, %s)",
                   (nombre, PAIS_MARCA[nombre]))
    ids_marca[nombre] = cursor.lastrowid

# Vendedores: particulares (personas) y profesionales (tiendas)
paises_vendedor = ["España", "Alemania", "Italia", "Francia", "Suiza", "Países Bajos"]
for _ in range(200):
    tipo = random.choices(["particular", "profesional"], weights=[60, 40])[0]
    if tipo == "particular":
        nombre = fake.name()
        correo = fake.unique.email()
    else:
        nombre = f"{random.choice(['Relojería', 'Joyería', 'Casa de Relojes'])} {fake.last_name()}"
        correo = fake.unique.company_email()
    cursor.execute(
        "INSERT INTO vendedores (nombre, tipo_vendedor, pais, correo) VALUES (%s, %s, %s, %s)",
        (nombre, tipo, random.choice(paises_vendedor), correo),
    )

# Compradores
paises_comprador = ["España", "México", "Colombia", "Argentina", "Chile", "Alemania"]
for _ in range(1000):
    cursor.execute(
        "INSERT INTO compradores (nombre_completo, correo, pais) VALUES (%s, %s, %s)",
        (fake.name(), fake.unique.email(), random.choice(paises_comprador)),
    )

# Anuncios: cada reloj es un modelo real con precio según su condición
factor_condicion = {"nuevo": 1.0, "sin uso": 0.95, "muy bueno": 0.88, "bueno": 0.80, "usado": 0.70}
anuncios = []  # (id_anuncio, fecha_publicacion)
for _ in range(2000):
    marca = random.choice(list(CATALOGO))
    modelo, pmin, pmax, *_ = random.choice(CATALOGO[marca])
    condicion = random.choices(list(factor_condicion), weights=[20, 10, 35, 25, 10])[0]
    precio = round(random.uniform(pmin, pmax) * factor_condicion[condicion], -1)
    fecha_pub = fake.date_time_between(start_date="-540d", end_date="-1d")
    cursor.execute(
        "INSERT INTO anuncios (id_vendedor, id_marca, modelo, condicion, precio_eur, fecha_publicacion) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (random.randint(1, 200), ids_marca[marca], modelo, condicion, precio, fecha_pub),
    )
    anuncios.append((cursor.lastrowid, fecha_pub))

# Pedidos: 800 anuncios con compra, siempre después de su publicación
for id_anuncio, fecha_pub in random.sample(anuncios, 800):
    cursor.execute("SELECT precio_eur FROM anuncios WHERE id_anuncio = %s", (id_anuncio,))
    precio = cursor.fetchone()[0]
    estado = random.choices(["completado", "en_envio", "cancelado"], weights=[60, 20, 20])[0]
    cursor.execute(
        "INSERT INTO pedidos (id_anuncio, id_comprador, fecha_pedido, total_eur, comision_eur, estado) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (id_anuncio, random.randint(1, 1000),
         fake.date_time_between(start_date=fecha_pub, end_date="now"),
         precio, round(float(precio) * 0.065, 2), estado),
    )
    # Un pedido cancelado no vende el reloj
    if estado != "cancelado":
        cursor.execute("UPDATE anuncios SET estado = 'vendido' WHERE id_anuncio = %s", (id_anuncio,))

conexion.commit()
conexion.close()
print("MySQL local poblado correctamente")