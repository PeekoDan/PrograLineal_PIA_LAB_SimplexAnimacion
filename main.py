import subprocess
import sys
import os

# =====================================
# PROGRAMA PRINCIPAL
# Este archivo se encarga de pedir los datos al usuario,
# validarlos, mostrarlos y lanzar la animacion de Manim.
# La logica del simplex y la animacion estan en simplex_manim.py.
# Ambos archivos deben estar en la misma carpeta para que funcione.
# =====================================


def pedir_coeficientes(mensaje):
    """
    Pide al usuario una fila de numeros separados por espacios.
    Repite la solicitud hasta que el usuario ingrese valores validos.
    Devuelve una lista de floats.
    """
    while True:
        try:
            valores = list(map(float, input(mensaje).split()))
            if len(valores) == 0:
                print("  Error: debe ingresar al menos un valor. Intente de nuevo.\n")
                continue
            return valores
        except ValueError:
            # Esto ocurre si el usuario escribe algo que no es un numero
            print("  Error: ingrese solo numeros separados por espacios. Intente de nuevo.\n")


def pedir_entero(mensaje):
    """
    Pide al usuario un numero entero positivo.
    Repite la solicitud si el valor no es valido.
    """
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
    """
    Muestra el problema de programacion lineal tal como fue capturado,
    en formato legible antes de confirmar y generar la animacion.
    """
    n = len(C)
    print("\n" + "="*50)
    print("  PROBLEMA CAPTURADO")
    print("="*50)

    # Construir el string de la funcion objetivo
    obj_str = " + ".join([f"{C[i]:.2f}x{i+1}" for i in range(n)])
    print(f"  max z = {obj_str}")
    print()
    print("  Sujeto a:")

    # Mostrar cada restriccion en formato legible
    for i, (fila, bi) in enumerate(zip(A, B)):
        rest_str = " + ".join([f"{fila[j]:.2f}x{j+1}" for j in range(n)])
        print(f"    {rest_str} <= {bi:.2f}")

    # Recordar al usuario la condicion de no negatividad
    print("    x1, x2 >= 0")
    print("="*50 + "\n")


# =====================================
# SOLICITUD DE DATOS
# Se pide primero la funcion objetivo y luego las restricciones.
# El numero de coeficientes de la funcion objetivo determina
# cuantos coeficientes se esperan en cada restriccion.
# =====================================

print("\n" + "="*50)
print("  METODO SIMPLEX - INGRESO DE DATOS")
print("="*50 + "\n")

# Pedir los coeficientes de la funcion objetivo
print("FUNCION OBJETIVO")
print("-" * 30)
C = pedir_coeficientes(
    "Imprima los coeficientes de la funcion objetivo\n"
    "en el orden correcto y un espacio entre ellos.\n> "
)

# El numero de variables queda definido por cuantos coeficientes se ingresaron
n = len(C)

print()
print("RESTRICCIONES")
print("-" * 30)

# Preguntar cuantas restricciones tiene el problema
m = pedir_entero(
    "Imprima el numero de restricciones\n> "
)

A = []  # matriz de coeficientes de las restricciones
B = []  # lados derechos de las restricciones

# Pedir cada restriccion por separado
for i in range(m):
    print(f"\nRestriccion {i+1}:")

    # Pedir los coeficientes del lado izquierdo
    fila = pedir_coeficientes(
        f"Imprima los {n} coeficientes de la restriccion {i+1}\n"
        f"en el orden correcto y un espacio entre ellos.\n> "
    )

    # Verificar que la cantidad de coeficientes coincida con las variables
    while len(fila) != n:
        print(f"  Error: se esperaban {n} coeficientes, se ingresaron {len(fila)}. Intente de nuevo.\n")
        fila = pedir_coeficientes(
            f"Imprima los {n} coeficientes de la restriccion {i+1}\n"
            f"en el orden correcto y un espacio entre ellos.\n> "
        )
    A.append(fila)

    # Pedir el lado derecho de esta restriccion
    bi = pedir_coeficientes(
        f"Imprima el lado derecho de la restriccion {i+1}.\n> "
    )
    B.append(bi[0])  # solo se toma el primer valor aunque el usuario ingrese varios

# Mostrar el problema completo antes de confirmar
imprimir_problema(C, A, B)

# Dar la oportunidad de corregir si algo estuvo mal
confirmacion = input("Los datos son correctos? (s/n): ").strip().lower()
if confirmacion != "s":
    print("\nOperacion cancelada. Vuelva a ejecutar el programa para reingresar los datos.")
    input("Presiona Enter para cerrar...")
    sys.exit(0)

# =====================================
# PASAR DATOS A LA ESCENA Y ANIMAR
# El problema de pasar datos a Manim es que la escena se instancia
# internamente y no acepta argumentos en el constructor.
# La solucion fue escribir los datos en un archivo temporal (_datos_simplex.py)
# y luego inyectarlos como atributos de clase en un runner (_runner_simplex.py).
# Ambos archivos se eliminan automaticamente al terminar.
# =====================================

# Ruta de los archivos temporales (en la misma carpeta que este script)
datos_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_datos_simplex.py")
runner_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_runner_simplex.py")

# Escribir los datos como variables de Python para que el runner pueda importarlos
with open(datos_path, "w") as f:
    f.write(f"C = {C}\n")
    f.write(f"A = {A}\n")
    f.write(f"B = {B}\n")

# Escribir el runner que importa los datos, los inyecta en la escena y la ejecuta
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

# Ejecutar el runner con el mismo interprete de Python que esta corriendo este script
result = subprocess.run(
    [sys.executable, runner_path],
    capture_output=False,
)

# Limpiar los archivos temporales sin importar si hubo error o no
for path in [datos_path, runner_path]:
    if os.path.exists(path):
        os.remove(path)

# Limpiar la consola y mostrar el resultado solo si todo salio bien
if result.returncode == 0:
    os.system("cls")
    print(f"\nAnimacion completada exitosamente!")

print(f"\nProceso terminado con codigo: {result.returncode}")
input("Presiona Enter para cerrar...")
