"""
funciones.py — Módulo de funciones auxiliares para el Zoológico.
Contiene: clase Animal, carga/escritura de CSV y lógica de listado.
"""

import csv
import os

COLUMNAS = [
    "nombre_animal", "pelo", "plumas", "huevos", "leche",
    "vuela", "acuatico", "depredador", "dientes", "espinazo",
    "respira", "venenoso", "aletas", "patas", "cola",
    "domestico", "tamanio_gato", "clase",
]

CARACTERISTICAS = [
    "pelo", "plumas", "huevos", "leche", "vuela", "acuatico",
    "depredador", "dientes", "espinazo", "respira", "venenoso",
    "aletas", "patas", "cola", "domestico", "tamanio_gato",
]


class Animal:
    """Representa un animal del zoológico con sus características."""

    def __init__(self, nombre_animal, pelo, plumas, huevos, leche,
                 vuela, acuatico, depredador, dientes, espinazo,
                 respira, venenoso, aletas, patas, cola,
                 domestico, tamanio_gato, clase):
        self.nombre_animal = str(nombre_animal)
        self.pelo = int(pelo)
        self.plumas = int(plumas)
        self.huevos = int(huevos)
        self.leche = int(leche)
        self.vuela = int(vuela)
        self.acuatico = int(acuatico)
        self.depredador = int(depredador)
        self.dientes = int(dientes)
        self.espinazo = int(espinazo)
        self.respira = int(respira)
        self.venenoso = int(venenoso)
        self.aletas = int(aletas)
        self.patas = int(patas)
        self.cola = int(cola)
        self.domestico = int(domestico)
        self.tamanio_gato = int(tamanio_gato)
        self.clase = int(clase)

    def __str__(self):
        caract = []
        for c in CARACTERISTICAS:
            val = getattr(self, c)
            if c == "patas":
                caract.append(f"patas={val}")
            elif val == 1:
                caract.append(c)
        return f"{self.nombre_animal} (clase {self.clase}) [{', '.join(caract)}]"

    def __repr__(self):
        vals = ", ".join(f"{c}={getattr(self, c)}" for c in COLUMNAS)
        return f"Animal({vals})"

    def a_dict(self):
        return {col: getattr(self, col) for col in COLUMNAS}

def cargar_csv(ruta):
    """
    Carga un archivo CSV en un diccionario.
    Retorna: dict  { valor_primera_columna : dict_fila }
    Funciona para clases.csv  (clave = Clase_id)
              y zoo.csv       (clave = nombre_animal).
    """
    datos = {}
    if not os.path.exists(ruta):
        return datos
    with open(ruta, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for fila in reader:
            clave = list(fila.values())[0]  
            datos[clave] = dict(fila)
    return datos


def guardar_csv(ruta, datos, fieldnames):
    """
    Escribe un diccionario de dicts en un archivo CSV.
    datos     : dict  { clave: dict_fila }
    fieldnames: lista de nombres de columnas
    """
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for fila in datos.values():
            writer.writerow(fila)

def dict_a_animales(datos_zoo):
    """Convierte el dict cargado por cargar_csv en una lista de objetos Animal."""
    animales = []
    for fila in datos_zoo.values():
        try:
            a = Animal(
                nombre_animal=fila["nombre_animal"],
                pelo=fila["pelo"],
                plumas=fila["plumas"],
                huevos=fila["huevos"],
                leche=fila["leche"],
                vuela=fila["vuela"],
                acuatico=fila["acuatico"],
                depredador=fila["depredador"],
                dientes=fila["dientes"],
                espinazo=fila["espinazo"],
                respira=fila["respira"],
                venenoso=fila["venenoso"],
                aletas=fila["aletas"],
                patas=fila["patas"],
                cola=fila["cola"],
                domestico=fila["domestico"],
                tamanio_gato=fila["tamanio_gato"],
                clase=fila["clase"],
            )
            animales.append(a)
        except (KeyError, ValueError):
            pass
    return animales


def animales_a_dict(animales):
    """Convierte lista de objetos Animal al formato dict para guardar_csv."""
    return {a.nombre_animal: a.a_dict() for a in animales}

def listar_por_clase(animales, clases, clase_id):
    """
    Retorna lista de animales cuya clase coincida con clase_id (int).
    Imprime el resultado en pantalla.
    """
    nombre_clase = clases.get(str(clase_id), {}).get("Clase_tipo", f"Clase {clase_id}")
    resultado = [a for a in animales if a.clase == clase_id]
    if not resultado:
        print(f"\n  No se encontraron animales en la clase '{nombre_clase}'.")
    else:
        print(f"\n  Animales de clase '{nombre_clase}' ({len(resultado)}):")
        print("  " + "─" * 50)
        for a in sorted(resultado, key=lambda x: x.nombre_animal):
            print(f"    • {a}")
    return resultado

def listar_por_caracteristica(animales, caracteristica, valor=1):
    """
    Retorna lista de animales que tengan la característica con el valor dado.
    Para 'patas' se compara con el número que ingrese el usuario.
    """
    resultado = [a for a in animales if getattr(a, caracteristica) == valor]
    if not resultado:
        print(f"\n  No se encontraron animales con {caracteristica}={valor}.")
    else:
        print(f"\n  Animales con {caracteristica}={valor} ({len(resultado)}):")
        print("  " + "─" * 50)
        for a in sorted(resultado, key=lambda x: x.nombre_animal):
            print(f"    • {a}")
    return resultado

def pedir_binario(prompt):
    """Pide un valor 0/1 al usuario."""
    while True:
        v = input(f"    {prompt} (0=No / 1=Sí): ").strip()
        if v in ("0", "1"):
            return int(v)
        print("    ⚠  Por favor ingresa 0 o 1.")


def agregar_animal(animales, clases):
    """Solicita datos al usuario e incorpora uno o más animales a la lista."""
    print("\n  ─── Agregar nuevo(s) animal(es) ───")
    while True:
        nombre = input("  Nombre del animal (o ENTER para terminar): ").strip().lower()
        if nombre == "":
            break
        if any(a.nombre_animal == nombre for a in animales):
            print(f"  ⚠  '{nombre}' ya existe en el zoológico.")
            continue

        print(f"\n  Ingresa las características de '{nombre}':")
        kwargs = {"nombre_animal": nombre}
        for c in CARACTERISTICAS:
            if c == "patas":
                while True:
                    v = input("    patas (número entero): ").strip()
                    if v.isdigit():
                        kwargs["patas"] = int(v)
                        break
                    print("    ⚠  Ingresa un número entero.")
            else:
                kwargs[c] = pedir_binario(c)

        print("\n  Clases disponibles:")
        for cid, cinfo in sorted(clases.items(), key=lambda x: int(x[0])):
            print(f"    {cid}. {cinfo['Clase_tipo']}")
        while True:
            cid = input("  Selecciona el número de clase: ").strip()
            if cid in clases:
                kwargs["clase"] = int(cid)
                break
            print("  ⚠  Clase inválida.")

        nuevo = Animal(**kwargs)
        animales.append(nuevo)
        print(f"  ✔  '{nombre}' agregado correctamente.\n")

    return animales
