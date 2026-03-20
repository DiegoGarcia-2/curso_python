"""
main.py — Lógica principal del Zoológico.
Ejecuta el menú interactivo y coordina todas las operaciones.
"""

import os
from funciones import (
    cargar_csv,
    guardar_csv,
    dict_a_animales,
    animales_a_dict,
    listar_por_clase,
    listar_por_caracteristica,
    agregar_animal,
    COLUMNAS,
    CARACTERISTICAS,
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RUTA_ZOO    = os.path.join(BASE_DIR, "data", "zoo.csv")
RUTA_CLASES = os.path.join(BASE_DIR, "data", "clases.csv")

def menu_principal():
    print("\n" + "═" * 55)
    print("          SISTEMA DE ZOOLÓGICO  ")
    print("═" * 55)
    print("  1. Listar animales por clasificación (clase)")
    print("  2. Listar animales por característica")
    print("  3. Agregar nuevo(s) animal(es)")
    print("  4. Salir (guarda cambios automáticamente)")
    print("═" * 55)
    return input("  Selecciona una opción: ").strip()

def menu_clases(clases):
    print("\n  ─── Clases disponibles ───")
    for cid, cinfo in sorted(clases.items(), key=lambda x: int(x[0])):
        print(f"    {cid}. {cinfo['Clase_tipo']}")
    opcion = input("  Ingresa el número de clase: ").strip()
    if opcion not in clases:
        print("    Opción inválida.")
        return None
    return int(opcion)

def menu_caracteristicas():
    print("\n  ─── Características disponibles ───")
    for i, c in enumerate(CARACTERISTICAS, 1):
        print(f"    {i:2}. {c}")
    opcion = input("  Ingresa el número de característica: ").strip()
    if not opcion.isdigit() or not (1 <= int(opcion) <= len(CARACTERISTICAS)):
        print("    Opción inválida.")
        return None, None

    caract = CARACTERISTICAS[int(opcion) - 1]

    if caract == "patas":
        v = input("  ¿Cuántas patas? (número entero): ").strip()
        if not v.isdigit():
            print("    Número inválido.")
            return None, None
        return caract, int(v)
    else:
        return caract, 1

def main():
    datos_clases = cargar_csv(RUTA_CLASES)   
    datos_zoo    = cargar_csv(RUTA_ZOO)      

    animales = dict_a_animales(datos_zoo)

    print(f"\n  ✔  {len(animales)} animales cargados | {len(datos_clases)} clases disponibles.")

    while True:
        opcion = menu_principal()

        if opcion == "1":
            clase_id = menu_clases(datos_clases)
            if clase_id is not None:
                listar_por_clase(animales, datos_clases, clase_id)

        elif opcion == "2":
            caract, valor = menu_caracteristicas()
            if caract is not None:
                listar_por_caracteristica(animales, caract, valor)

        elif opcion == "3":
            animales = agregar_animal(animales, datos_clases)

        elif opcion == "4":
            print("\n  Guardando cambios en zoo.csv …", end=" ")
            guardar_csv(RUTA_ZOO, animales_a_dict(animales), fieldnames=COLUMNAS)
            print("✔  ¡Hasta luego!")
            break

        else:
            print("    Opción no válida. Elige entre 1 y 4.")

if __name__ == "__main__":
    main()
