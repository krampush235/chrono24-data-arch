import os
import random
import pymysql
from pymongo import MongoClient
from faker import Faker
from dotenv import load_dotenv

load_dotenv()
fake = Faker("es_ES")

# Leer los IDs reales de MySQL para que las dos bases se puedan cruzar después
conexion = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASS"),
    database=os.getenv("MYSQL_DB"),
)
cursor = conexion.cursor()
cursor.execute("SELECT id_anuncio FROM anuncios")
ids_anuncios = [fila[0] for fila in cursor.fetchall()]
cursor.execute("SELECT id_comprador FROM compradores")
ids_compradores = [fila[0] for fila in cursor.fetchall()]
cursor.execute("SELECT id_vendedor FROM vendedores")
ids_vendedores = [fila[0] for fila in cursor.fetchall()]
conexion.close()

# Conexión a MongoDB Atlas
cliente = MongoClient(os.getenv("MONGO_URI"))
bd = cliente["chrono_nosql"]

# Limpiar colecciones por si se ejecuta de nuevo
for nombre in ["detalle_anuncios", "resenas", "favoritos", "eventos_navegacion"]:
    bd[nombre].drop()

# Detalle de cada reloj (atributos variables)
detalles = []
for id_anuncio in ids_anuncios:
    doc = {
        "id_anuncio": id_anuncio,
        "movimiento": random.choice(["Automático", "Manual", "Cuarzo"]),
        "material_caja": random.choice(["Acero", "Oro", "Titanio", "Platino"]),
        "diametro_mm": random.choice([36, 38, 40, 41, 42, 44]),
        "anio": random.randint(1960, 2024),
        "contenido_entrega": random.sample(
            ["caja original", "papeles", "certificado", "correa extra"],
            k=random.randint(0, 3)),
        "imagenes": [f"img{i}.jpg" for i in range(random.randint(2, 6))],
    }
    # Solo algunos relojes tienen extras: esto es lo flexible de NoSQL
    if random.random() < 0.4:
        doc["extras"] = {
            "taquimetro": random.choice([True, False]),
            "resistencia_agua_m": random.choice([30, 50, 100, 300]),
        }
    detalles.append(doc)
bd.detalle_anuncios.insert_many(detalles)

# Reseñas de vendedores
bd.resenas.insert_many([{
    "id_vendedor": random.choice(ids_vendedores),
    "id_comprador": random.choice(ids_compradores),
    "calificacion": random.randint(1, 5),
    "comentario": fake.sentence(),
    "fecha": fake.date_between(start_date="-1y").isoformat(),
} for _ in range(1500)])

# Favoritos de los compradores
bd.favoritos.insert_many([{
    "id_comprador": c,
    "ids_anuncios": random.sample(ids_anuncios, k=random.randint(1, 8)),
} for c in random.sample(ids_compradores, 400)])

# Eventos de navegación
bd.eventos_navegacion.insert_many([{
    "id_sesion": fake.uuid4()[:8],
    "id_comprador": random.choice(ids_compradores),
    "evento": random.choice(["ver_anuncio", "busqueda", "agregar_favorito", "contactar_vendedor"]),
    "id_anuncio": random.choice(ids_anuncios),
    "fecha_hora": fake.date_time_between(start_date="-6M").isoformat(),
    "dispositivo": random.choice(["movil", "escritorio", "tableta"]),
} for _ in range(10000)])

print("MongoDB Atlas poblado correctamente")