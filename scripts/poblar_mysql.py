import os
import random
import pymysql
from faker import Faker
from dotenv import load_dotenv

load_dotenv()
fake = Faker("es_ES")

# Conexión a MySQL local
conexion = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASS"),
    database=os.getenv("MYSQL_DB"),
)
cursor = conexion.cursor()

# Marcas
marcas = [
    ("Rolex", "Suiza"), ("Omega", "Suiza"), ("Patek Philippe", "Suiza"),
    ("Audemars Piguet", "Suiza"), ("Cartier", "Francia"),
    ("Seiko", "Japón"), ("TAG Heuer", "Suiza"), ("IWC", "Suiza"),
]
cursor.executemany("INSERT INTO marcas (nombre, pais) VALUES (%s, %s)", marcas)

# Vendedores (200)
for _ in range(200):
    cursor.execute(
        "INSERT INTO vendedores (nombre, tipo_vendedor, pais, correo) VALUES (%s, %s, %s, %s)",
        (fake.company(), random.choice(["particular", "profesional"]),
         random.choice(["España", "Alemania", "Italia", "Francia"]),
         fake.unique.email()),
    )

# Compradores (1000)
for _ in range(1000):
    cursor.execute(
        "INSERT INTO compradores (nombre_completo, correo, pais) VALUES (%s, %s, %s)",
        (fake.name(), fake.unique.email(),
         random.choice(["España", "México", "Colombia", "Alemania"])),
    )

# Anuncios (2000)
for _ in range(2000):
    cursor.execute(
        "INSERT INTO anuncios (id_vendedor, id_marca, modelo, condicion, precio_eur) "
        "VALUES (%s, %s, %s, %s, %s)",
        (random.randint(1, 200), random.randint(1, 8),
         f"Modelo {fake.bothify('??-###')}",
         random.choice(["nuevo", "sin uso", "muy bueno", "bueno", "usado"]),
         round(random.uniform(800, 60000), 2)),
    )

# Pedidos (800 anuncios vendidos)
cursor.execute("SELECT id_anuncio, precio_eur FROM anuncios ORDER BY RAND() LIMIT 800")
for id_anuncio, precio in cursor.fetchall():
    cursor.execute(
        "INSERT INTO pedidos (id_anuncio, id_comprador, fecha_pedido, total_eur, comision_eur, estado) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (id_anuncio, random.randint(1, 1000),
         fake.date_time_between(start_date="-1y", end_date="now"),
         precio, round(float(precio) * 0.065, 2),
         random.choice(["completado", "completado", "completado", "en_envio", "cancelado"])),
    )
    cursor.execute("UPDATE anuncios SET estado = 'vendido' WHERE id_anuncio = %s", (id_anuncio,))

conexion.commit()
conexion.close()
print("MySQL local poblado correctamente")