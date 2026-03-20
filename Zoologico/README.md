Alumno: Diego Andrés García González
Proyecto: Zoológico

Pasos para ejecutar el programa:

1. Abre una terminal y navega al directorio raíz del proyecto:

```bash
cd zoologico
```

2. Ejecuta el programa:

```bash
python main.py
```

---

## Cómo interactuar con el programa

Al iniciar verás el menú principal:

═══════════════════════════════════════════════════════
          SISTEMA DE ZOOLÓGICO  
═══════════════════════════════════════════════════════
  1. Listar animales por clasificación (clase)
  2. Listar animales por característica
  3. Agregar nuevo(s) animal(es)
  4. Salir (guarda cambios automáticamente)
═══════════════════════════════════════════════════════


Opción 1 — Listar por clase

Se muestran las 7 clases disponibles (Mamífero, Ave, Reptil, Pez, Anfibio, Insecto, Invertebrado). Ingresa el número para ver todos los animales de esa clase.

Opción 2 — Listar por característica

Se listan las 16 características disponibles (pelo, plumas, huevos, vuela, acuatico, etc.). Ingresa el número de la característica. Para `patas` se te pedirá cuántas patas filtrar; para el resto se buscan animales que **posean** esa característica (valor = 1).

Opción 3 — Agregar animal(es)

Se solicita:
- **Nombre** del animal
- **Valor (0/1)** para cada característica
- **Número de patas** (entero)
- **Clase** a la que pertenece

Puedes agregar varios animales consecutivos. Deja el nombre en blanco y presiona ENTER para terminar.

Opción 4 — Salir

Guarda todos los cambios realizados en `data/zoo.csv` antes de cerrar. La próxima vez que inicies el programa los nuevos animales estarán disponibles.
