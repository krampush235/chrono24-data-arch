# Catálogo de referencia: marca -> lista de modelos
# (modelo, precio_min, precio_max, diámetros_mm, movimiento, materiales, resistencia_agua_m)
# Los precios son aproximados y solo sirven para generar datos simulados.

PAIS_MARCA = {
    "Rolex": "Suiza", "Omega": "Suiza", "Patek Philippe": "Suiza",
    "Audemars Piguet": "Suiza", "Cartier": "Francia",
    "Seiko": "Japón", "TAG Heuer": "Suiza", "IWC": "Suiza",
}

CATALOGO = {
    "Rolex": [
        ("Submariner Date", 9000, 16000, [40, 41], "Automático", ["Acero"], 300),
        ("Datejust 36", 6500, 12000, [36], "Automático", ["Acero", "Oro"], 100),
        ("GMT-Master II", 12000, 22000, [40], "Automático", ["Acero"], 100),
        ("Daytona", 25000, 45000, [40], "Automático", ["Acero", "Oro"], 100),
        ("Oyster Perpetual 41", 6000, 9500, [41], "Automático", ["Acero"], 100),
    ],
    "Omega": [
        ("Speedmaster Professional", 4500, 7500, [42], "Manual", ["Acero"], 50),
        ("Seamaster Diver 300M", 3500, 6000, [42], "Automático", ["Acero", "Titanio"], 300),
        ("Constellation", 2500, 5000, [39], "Automático", ["Acero", "Oro"], 50),
        ("De Ville Prestige", 1500, 3000, [36], "Automático", ["Acero"], 30),
    ],
    "Patek Philippe": [
        ("Nautilus 5711", 80000, 150000, [40], "Automático", ["Acero"], 120),
        ("Calatrava 5196", 18000, 30000, [37], "Manual", ["Oro"], 30),
        ("Aquanaut 5167", 30000, 60000, [40], "Automático", ["Acero"], 120),
    ],
    "Audemars Piguet": [
        ("Royal Oak 15500", 28000, 45000, [41], "Automático", ["Acero"], 50),
        ("Royal Oak Offshore", 25000, 40000, [42], "Automático", ["Acero", "Titanio"], 100),
        ("Code 11.59", 22000, 35000, [41], "Automático", ["Oro"], 30),
    ],
    "Cartier": [
        ("Tank Must", 2500, 4000, [33], "Cuarzo", ["Acero"], 30),
        ("Santos de Cartier", 5500, 9000, [39], "Automático", ["Acero", "Oro"], 100),
        ("Ballon Bleu", 4500, 8000, [36], "Automático", ["Acero", "Oro"], 30),
    ],
    "Seiko": [
        ("Presage Cocktail Time", 300, 600, [40], "Automático", ["Acero"], 50),
        ("Prospex Turtle", 400, 700, [45], "Automático", ["Acero"], 200),
        ("5 Sports", 150, 350, [42], "Automático", ["Acero"], 100),
        ("Astron GPS Solar", 1000, 2000, [42], "Cuarzo", ["Titanio"], 100),
    ],
    "TAG Heuer": [
        ("Carrera", 2500, 5000, [39, 41], "Automático", ["Acero"], 100),
        ("Aquaracer", 1500, 3000, [43], "Automático", ["Acero"], 300),
        ("Monaco", 4000, 7000, [39], "Automático", ["Acero"], 100),
    ],
    "IWC": [
        ("Portugieser Chronograph", 5000, 9000, [41], "Automático", ["Acero", "Oro"], 30),
        ("Pilot's Watch Mark XX", 3500, 6000, [40], "Automático", ["Acero"], 60),
        ("Portofino", 3000, 5500, [40], "Automático", ["Acero", "Oro"], 30),
    ],
}


def buscar_modelo(marca, modelo):
    for datos in CATALOGO[marca]:
        if datos[0] == modelo:
            return datos