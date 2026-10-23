import os
import random
from datetime import datetime, timedelta
import pymysql
from pymongo import MongoClient
from faker import Faker
from dotenv import load_dotenv
from catalogo import CATALOGO, buscar_modelo

load_dotenv()
fake = Faker("es_ES")

# ---------------------------------------------------------------
# 1) Leer de MySQL los datos reales, para que ambas bases coincidan
# ---------------------------------------------------------------
conexion = pymysql.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASS"),
    database=os.getenv("MYSQL_DB"),
)
cursor = conexion.cursor()

cursor.execute("""SELECT a.id_anuncio, m.nombre, a.modelo, a.condicion, a.estado
                  FROM anuncios a JOIN marcas m ON m.id_marca = a.id_marca""")
lista_anuncios = cursor.fetchall()

cursor.execute("SELECT id_comprador FROM compradores")
ids_compradores = [fila[0] for fila in cursor.fetchall()]

cursor.execute("""SELECT a.id_vendedor, p.id_comprador, p.fecha_pedido
                  FROM pedidos p JOIN anuncios a ON a.id_anuncio = p.id_anuncio
                  WHERE p.estado = 'completado'""")
pedidos_completados = cursor.fetchall()
conexion.close()

ids_anuncios_activos = [a[0] for a in lista_anuncios if a[4] == "activo"]

# ---------------------------------------------------------------
# 2) Conectar a MongoDB Atlas y limpiar las colecciones
# ---------------------------------------------------------------
base_datos = MongoClient(os.getenv("MONGO_URI"))["chrono_nosql"]
for nombre_coleccion in ["detalle_anuncios", "resenas", "favoritos", "eventos_navegacion"]:
    base_datos[nombre_coleccion].drop()


def formatear_nombre_archivo(texto):
    return texto.lower().replace(" ", "_").replace("'", "")


# ---------------------------------------------------------------
# 3) Detalle de cada reloj (atributos que varían de un reloj a otro)
# ---------------------------------------------------------------
modelos_cronografo = ["Daytona", "Speedmaster", "Carrera", "Monaco", "Chronograph", "Offshore"]
opciones_entrega = ["caja original", "papeles", "certificado de garantía", "correa adicional"]

detalles = []
for id_anuncio, marca, modelo, condicion, estado in lista_anuncios:
    _, _, _, diametros, movimiento, materiales, resistencia_agua = buscar_modelo(marca, modelo)
    material = random.choice(materiales)
    diametro = random.choice(diametros)

    if condicion in ("nuevo", "sin uso"):
        anio = random.randint(2022, 2026)
        contenido_entrega = ["caja original", "papeles", "certificado de garantía"]
    else:
        anio = random.randint(1995, 2021)
        contenido_entrega = random.sample(opciones_entrega, k=random.randint(0, 3))

    detalle = {
        "id_anuncio": id_anuncio,
        "marca": marca,
        "modelo": modelo,
        "descripcion": f"{marca} {modelo} en condición {condicion}, con movimiento "
                       f"{movimiento.lower()} y caja de {material.lower()} de {diametro} mm.",
        "movimiento": movimiento,
        "material_caja": material,
        "diametro_mm": diametro,
        "anio": anio,
        "contenido_entrega": contenido_entrega,
        "imagenes": [f"{formatear_nombre_archivo(marca)}_{formatear_nombre_archivo(modelo)}_{n}.jpg"
                     for n in range(1, random.randint(3, 6))],
    }

    # Solo algunos relojes tienen extras: esto es lo flexible de NoSQL
    es_cronografo = any(palabra in modelo for palabra in modelos_cronografo)
    if es_cronografo or random.random() < 0.6:
        detalle["extras"] = {"resistencia_agua_m": resistencia_agua}
        if es_cronografo:
            detalle["extras"]["cronografo"] = True

    detalles.append(detalle)

base_datos.detalle_anuncios.insert_many(detalles)

# ---------------------------------------------------------------
# 4) Reseñas: solo de pedidos completados, con comentario acorde a la nota
# ---------------------------------------------------------------
comentarios_por_nota = {
    5: ["Reloj tal como en las fotos, embalaje impecable y envío rápido. Totalmente recomendable.",
        "Vendedor muy atento, resolvió todas mis dudas antes de comprar. Volvería a comprarle.",
        "Excelente experiencia, el reloj llegó con caja y papeles originales.",
        "Compra segura y trato profesional. El reloj está en perfecto estado."],
    4: ["Buen vendedor, el reloj está como se describía aunque el envío tardó algo más de lo previsto.",
        "Todo correcto en general, aunque había pequeños detalles estéticos que no se veían en las fotos.",
        "Buena comunicación y reloj en buen estado. Lo recomiendo."],
    3: ["El reloj corresponde a la descripción, pero la comunicación con el vendedor fue lenta.",
        "Compra aceptable. El embalaje era mejorable y tardó en llegar."],
    2: ["El estado del reloj era peor de lo anunciado y hubo que negociar una compensación.",
        "Poca respuesta del vendedor y envío con retraso."],
    1: ["El reloj no coincidía con la descripción y tuve que iniciar una devolución.",
        "No recomiendo a este vendedor, no respondió a mis mensajes."],
}

resenas = []
for id_vendedor, id_comprador, fecha_pedido in pedidos_completados:
    # No todos los compradores dejan reseña
    if random.random() < 0.85:
        calificacion = random.choices([5, 4, 3, 2, 1], weights=[55, 25, 10, 6, 4])[0]
        fecha_resena = min(fecha_pedido + timedelta(days=random.randint(3, 15)), datetime.now())
        resenas.append({
            "id_vendedor": id_vendedor,
            "id_comprador": id_comprador,
            "calificacion": calificacion,
            "comentario": random.choice(comentarios_por_nota[calificacion]),
            "fecha": fecha_resena.date().isoformat(),
        })

base_datos.resenas.insert_many(resenas)

# ---------------------------------------------------------------
# 5) Favoritos de los compradores (solo anuncios que siguen activos)
# ---------------------------------------------------------------
favoritos = []
for id_comprador in random.sample(ids_compradores, 400):
    favoritos.append({
        "id_comprador": id_comprador,
        "ids_anuncios": random.sample(ids_anuncios_activos, k=random.randint(1, 8)),
    })

base_datos.favoritos.insert_many(favoritos)

# ---------------------------------------------------------------
# 6) Eventos de navegación (visitas, búsquedas, contactos)
# ---------------------------------------------------------------
terminos_busqueda = [f"{marca} {datos[0]}" for marca in CATALOGO for datos in CATALOGO[marca]]

eventos = []
for _ in range(10000):
    tipo_evento = random.choices(
        ["ver_anuncio", "busqueda", "agregar_favorito", "contactar_vendedor"],
        weights=[55, 25, 12, 8],
    )[0]

    evento = {
        "id_sesion": fake.uuid4()[:8],
        "id_comprador": random.choice(ids_compradores),
        "evento": tipo_evento,
        "fecha_hora": fake.date_time_between(start_date="-180d").isoformat(),
        "dispositivo": random.choice(["móvil", "escritorio", "tableta"]),
    }

    if tipo_evento == "busqueda":
        evento["termino_busqueda"] = random.choice(terminos_busqueda)
    else:
        evento["id_anuncio"] = random.choice(ids_anuncios_activos)

    eventos.append(evento)

base_datos.eventos_navegacion.insert_many(eventos)

print("MongoDB Atlas poblado correctamente")