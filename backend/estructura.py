import os

IGNORAR = {
    "venv",
    ".venv",
    "__pycache__",
    ".git",
    "site-packages",
    "node_modules"
}

SALIDA = "estructura_proyecto.txt"

def mostrar_estructura(ruta, archivo, nivel=0, max_nivel=5):
    if nivel > max_nivel:
        return

    try:
        elementos = sorted(os.listdir(ruta))
    except PermissionError:
        return

    for elemento in elementos:
        if elemento in IGNORAR or elemento.startswith("."):
            continue

        linea = "│   " * nivel + "├── " + elemento
        archivo.write(linea + "\n")

        ruta_completa = os.path.join(ruta, elemento)
        if os.path.isdir(ruta_completa):
            mostrar_estructura(ruta_completa, archivo, nivel + 1, max_nivel)

if __name__ == "__main__":
    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write("📁 Estructura del proyecto\n\n")
        mostrar_estructura(".", f)

    print(f"✅ Estructura guardada automáticamente en '{SALIDA}'")
