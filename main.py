import subprocess
import sys
import os

# =====================================
# PROGRAMA PRINCIPAL
# Solicita los datos del problema y lanza la animacion.
# Guarda este archivo en la misma carpeta que simplex_manim.py
# =====================================

def pedir_coeficientes(mensaje):
    """Pide una fila de coeficientes separados por espacios y los devuelve como lista de floats."""
    while True:
        try:
            valores = list(map(float, input(mensaje).split()))
            if len(valores) == 0:
                print("  Error: debe ingresar al menos un valor. Intente de nuevo.\n")
                continue
            return valores
        except ValueError:
            print("  Error: ingrese solo numeros separados por espacios. Intente de nuevo.\n")


def pedir_entero(mensaje):
    """Pide un numero entero positivo."""
    while True:
        try:
            valor = int(input(mensaje))
            if valor <= 0:
                print("  Error: debe ser un numero entero positivo. Intente de nuevo.\n")
                continue
            return valor
        except ValueError:
            print("  Error: ingrese un numero entero. Intente de nuevo.\n")


def imprimir_problema(C, A, B):
    """Muestra el problema tal como fue capturado."""
    n = len(C)
    print("\n" + "="*50)
    print("  PROBLEMA CAPTURADO")
    print("="*50)

    obj_str = " + ".join([f"{C[i]:.2f}x{i+1}" for i in range(n)])
    print(f"  max z = {obj_str}")
    print()
    print("  Sujeto a:")
    for i, (fila, bi) in enumerate(zip(A, B)):
        rest_str = " + ".join([f"{fila[j]:.2f}x{j+1}" for j in range(n)])
        print(f"    {rest_str} <= {bi:.2f}")
    print("    x1, x2 >= 0")
    print("="*50 + "\n")


# =====================================
# SOLICITUD DE DATOS
# =====================================

print("\n" + "="*50)
print("  METODO SIMPLEX — INGRESO DE DATOS")
print("="*50 + "\n")

print("FUNCION OBJETIVO")
print("-" * 30)
C = pedir_coeficientes(
    "Imprima los coeficientes de la funcion objetivo\n"
    "en el orden correcto y un espacio entre ellos.\n> "
)
n = len(C)

print()
print("RESTRICCIONES")
print("-" * 30)
m = pedir_entero(
    "Imprima el numero de restricciones\n> "
)

A = []
B = []

for i in range(m):
    print(f"\nRestriccion {i+1}:")
    fila = pedir_coeficientes(
        f"Imprima los {n} coeficientes de la restriccion {i+1}\n"
        f"en el orden correcto y un espacio entre ellos.\n> "
    )
    # Asegurarse de que tenga exactamente n coeficientes
    while len(fila) != n:
        print(f"  Error: se esperaban {n} coeficientes, se ingresaron {len(fila)}. Intente de nuevo.\n")
        fila = pedir_coeficientes(
            f"Imprima los {n} coeficientes de la restriccion {i+1}\n"
            f"en el orden correcto y un espacio entre ellos.\n> "
        )
    A.append(fila)

    bi = pedir_coeficientes(
        f"Imprima el lado derecho de la restriccion {i+1}.\n> "
    )
    B.append(bi[0])

# Mostrar el problema capturado antes de animar
imprimir_problema(C, A, B)

confirmacion = input("¿Los datos son correctos? (s/n): ").strip().lower()
if confirmacion != "s":
    print("\nOperacion cancelada. Vuelva a ejecutar el programa para reingresar los datos.")
    input("Presiona Enter para cerrar...")
    sys.exit(0)

# =====================================
# PASAR DATOS A LA ESCENA Y ANIMAR
# =====================================

# Escribir un archivo temporal con los datos para que simplex_manim.py los lea
datos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_datos_simplex.py")
with open(datos_path, "w") as f:
    f.write(f"C = {C}\n")
    f.write(f"A = {A}\n")
    f.write(f"B = {B}\n")

# Crear un runner temporal que inyecta los datos y lanza la escena
runner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_runner_simplex.py")
with open(runner_path, "w") as f:
    f.write("from _datos_simplex import C, A, B\n")
    f.write("from simplex_manim import SimplexScene\n")
    f.write("from manim import tempconfig\n")
    f.write("SimplexScene.C = C\n")
    f.write("SimplexScene.A = A\n")
    f.write("SimplexScene.B = B\n")
    f.write("with tempconfig({'quality': 'low_quality', 'preview': True}):\n")
    f.write("    scene = SimplexScene()\n")
    f.write("    scene.render()\n")

print("\nGenerando animacion, por favor espere...\n")

result = subprocess.run(
    [sys.executable, runner_path],
    capture_output=False,
)

# Limpiar archivos temporales
for path in [datos_path, runner_path]:
    if os.path.exists(path):
        os.remove(path)

if result.returncode==0:
    os.system(cls)
    print(f"\n¡Animación completada!")
print(f"\nProceso terminado con codigo: {result.returncode}")
input("Presiona Enter para cerrar...")
