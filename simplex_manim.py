import numpy as np
from manim import *

# =====================================
# SIMPLEX
# Implementacion del metodo simplex para maximizacion.
# Recibe A (matriz de restricciones), b (lados derechos)
# y c (coeficientes de la funcion objetivo).
# Devuelve la solucion optima, el valor optimo, el tableau
# final y la lista de puntos visitados en cada iteracion.
# =====================================

def simplex_max(A, b, c):
    # Convertir todo a arreglos de numpy con tipo float
    # para evitar problemas de division entera
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    m, n = A.shape  # m = numero de restricciones, n = numero de variables

    # Construir el tableau inicial del metodo simplex
    # El tableau tiene forma (m+1) x (n+m+1):
    #   - m filas para las restricciones
    #   - 1 fila para la funcion objetivo (ultima fila)
    #   - n columnas para variables originales
    #   - m columnas para variables de holgura
    #   - 1 columna para el lado derecho
    tableau = np.zeros((m + 1, n + m + 1))
    tableau[:m, :n] = A                  # coeficientes de las variables originales
    tableau[:m, n:n + m] = np.eye(m)    # variables de holgura (matriz identidad)
    tableau[:m, -1] = b                  # lados derechos de las restricciones
    tableau[-1, :n] = -c                 # fila z: negativo de c porque maximizamos

    # Nombres de todas las variables para rastrear la base
    var_names = [f"x{i+1}" for i in range(n)] + [f"s{i+1}" for i in range(m)]

    # Al inicio, las variables basicas son todas las de holgura
    basic_vars = [f"s{i+1}" for i in range(m)]

    # Guardar los puntos que visita el simplex en cada iteracion
    # El punto inicial es el origen (todas las variables originales en 0)
    points = []
    points.append(np.zeros(n))

    # Iteraciones del metodo simplex
    while True:
        # La fila z es la ultima fila, sin la columna del lado derecho
        z_row = tableau[-1, :-1]

        # La variable que entra es la de coeficiente mas negativo en z
        # (regla estandar de seleccion de columna pivote)
        entering_col = np.argmin(z_row)

        # Si no hay coeficientes negativos, la solucion actual es optima
        if z_row[entering_col] >= 0:
            break

        # Prueba del cociente minimo para elegir la variable que sale
        # Solo se consideran filas con coeficiente positivo en la columna pivote
        ratios = []
        for i in range(m):
            col_val = tableau[i, entering_col]
            if col_val > 0:
                ratios.append(tableau[i, -1] / col_val)
            else:
                # Cociente infinito: esta fila no puede ser pivote
                ratios.append(np.inf)

        # La fila con el menor cociente es la fila pivote (variable que sale)
        leaving_row = np.argmin(ratios)

        # Si todos los cocientes son infinito, el problema no tiene solucion acotada
        if ratios[leaving_row] == np.inf:
            raise ValueError("Problema no acotado")

        # Actualizar la lista de variables basicas con el intercambio
        basic_vars[leaving_row] = var_names[entering_col]

        # Operaciones de fila para hacer el elemento pivote igual a 1
        pivot = tableau[leaving_row, entering_col]
        tableau[leaving_row, :] /= pivot

        # Hacer cero todos los demas elementos en la columna pivote
        for i in range(m + 1):
            if i != leaving_row:
                tableau[i, :] -= tableau[i, entering_col] * tableau[leaving_row, :]

        # Leer la solucion actual desde el tableau
        # Solo nos interesan las variables originales (x), no las de holgura
        current_solution = np.zeros(n)
        for i in range(m):
            var = basic_vars[i]
            if var.startswith("x"):
                idx = int(var[1:]) - 1      # indice en base 0
                current_solution[idx] = tableau[i, -1]

        # Guardar este punto para animarlo despues
        points.append(current_solution.copy())

    # Leer la solucion optima final del tableau
    solution = np.zeros(n)
    for i in range(m):
        var = basic_vars[i]
        if var.startswith("x"):
            idx = int(var[1:]) - 1
            solution[idx] = tableau[i, -1]

    # El valor optimo esta en la esquina inferior derecha del tableau
    optimal_value = tableau[-1, -1]

    return solution, optimal_value, tableau, points


# =====================================
# FUNCION: calcular_vertices
# Calcula los vertices de la region factible definida por
# A_np @ x <= b_np, x >= 0, mas restricciones extra opcionales.
# Los vertices se obtienen intersectando pares de restricciones
# y verificando que el punto satisfaga todas las demas.
# Tambien se revisan intersecciones con los ejes coordenados.
# =====================================

def calcular_vertices(A_np, b_np, restricciones_extra=None):

    # Si hay restricciones extra, agregarlas al sistema antes de calcular
    # Esto se usa para "cortar" la region en cada iteracion del simplex
    if restricciones_extra:
        A_total = np.vstack([A_np] + [r[0] for r in restricciones_extra])
        b_total = np.concatenate([b_np] + [r[1] for r in restricciones_extra])
    else:
        A_total = A_np
        b_total = b_np

    m = len(A_total)
    vertices = []

    # Interseccion entre cada par de restricciones
    # Resolvemos el sistema 2x2 formado por dos restricciones
    for i in range(m):
        for j in range(i + 1, m):
            A_sub = np.array([A_total[i], A_total[j]])
            b_sub = np.array([b_total[i], b_total[j]])

            # Solo resolver si el sistema tiene solucion unica (det != 0)
            if abs(np.linalg.det(A_sub)) > 1e-10:
                sol_v = np.linalg.solve(A_sub, b_sub)

                # Verificar que el punto este en el cuadrante positivo
                # y que satisfaga todas las restricciones del sistema
                if np.all(sol_v >= -1e-6) and np.all(A_total @ sol_v <= b_total + 1e-6):
                    vertices.append(np.round(sol_v, 2))

    # Intersecciones de cada restriccion con los ejes coordenados
    # Eje x: hacer y=0 y despejar x
    # Eje y: hacer x=0 y despejar y
    for i in range(m):
        a1, a2 = A_total[i, 0], A_total[i, 1]
        bi = b_total[i]

        if a1 > 1e-10:
            p = np.array([bi / a1, 0.0])   # intercepto con eje x
            if np.all(A_total @ p <= b_total + 1e-6):
                vertices.append(np.round(p, 2))

        if a2 > 1e-10:
            p = np.array([0.0, bi / a2])   # intercepto con eje y
            if np.all(A_total @ p <= b_total + 1e-6):
                vertices.append(np.round(p, 2))

    # Intersecciones de las restricciones EXTRA con los ejes
    # Esto es necesario para que el corte de la region se vea bien en los bordes.
    # Esta fue la unica forma que halle de que los cortes en los ejes se representaran
    # correctamente, ya que el loop anterior no alcanza a detectarlos cuando
    # la restriccion extra tiene coeficientes negativos.
    if restricciones_extra:
        for a_extra, b_extra in restricciones_extra:
            a1, a2 = a_extra[0, 0], a_extra[0, 1]
            bi = b_extra[0]

            if abs(a1) > 1e-10:
                p = np.array([bi / a1, 0.0])
                if p[0] >= -1e-6 and np.all(A_total @ p <= b_total + 1e-6):
                    vertices.append(np.round(p, 2))

            if abs(a2) > 1e-10:
                p = np.array([0.0, bi / a2])
                if p[1] >= -1e-6 and np.all(A_total @ p <= b_total + 1e-6):
                    vertices.append(np.round(p, 2))

    # El origen siempre es un candidato a vertice si satisface todas las restricciones
    origen = np.array([0.0, 0.0])
    if np.all(A_total @ origen <= b_total + 1e-6):
        vertices.append(origen)

    # Si no hay vertices, devolver un arreglo vacio con forma correcta
    if len(vertices) == 0:
        return np.array([]).reshape(0, 2)

    # Eliminar duplicados que puedan haberse generado por multiples intersecciones
    vertices = np.unique(np.round(vertices, 6), axis=0)

    # Ordenar los vertices en sentido antihorario usando angulos desde el centroide
    # Esto es necesario para que Polygon de Manim dibuje el poligono correctamente
    # sin que se crucen los lados
    if len(vertices) > 2:
        center = np.mean(vertices, axis=0)
        angles = np.arctan2(vertices[:, 1] - center[1], vertices[:, 0] - center[0])
        vertices = vertices[np.argsort(angles)]

    return vertices


# =====================================
# FUNCION: calcular_escala
# Determina los limites de los ejes de forma automatica.
# Analiza los vertices reales de la region factible en lugar
# de usar un valor fijo de b, lo que da una escala mas ajustada.
# Se aplica un margen del 30% para que nada quede en el borde.
# Se usa la misma escala en ambos ejes para no distorsionar
# la forma de la region factible.
# =====================================

def calcular_escala(A_np, b_np, margen=1.3):
    vertices = calcular_vertices(A_np, b_np)

    # Caso degenerado: si no hay vertices, usar el mayor valor de b
    if len(vertices) == 0:
        escala = float(max(b_np) * margen)
        return escala, escala

    # Encontrar el maximo en cada eje entre todos los vertices
    x_max_real = float(np.max(vertices[:, 0]))
    y_max_real = float(np.max(vertices[:, 1]))

    # Aplicar margen y asegurar que la escala nunca sea cero
    x_max = max(x_max_real * margen, 1.0)
    y_max = max(y_max_real * margen, 1.0)

    # Escala uniforme: tomar el mayor de los dos para que ambos ejes sean iguales
    # Esto evita que la region factible se vea estirada o aplastada
    escala_uniforme = max(x_max, y_max)

    return escala_uniforme, escala_uniforme


# =====================================
# ESCENA MANIM
# Clase principal que genera la animacion del metodo simplex.
# C, A y B se inyectan como atributos de clase desde el runner
# antes de llamar a render(), ya que Manim instancia la escena
# internamente y no permite pasar argumentos al constructor.
# =====================================

class SimplexScene(Scene):
    # Valores por defecto vacios; se sobreescriben desde el runner
    C = []
    A = []
    B = []

    def construct(self):
        # Leer los datos inyectados desde afuera
        C = self.__class__.C
        A = self.__class__.A
        B = self.__class__.B

        # Resolver el problema antes de animar para tener todos los puntos listos
        sol, z_opt, tab, points = simplex_max(A, B, C)

        # Convertir a numpy para operaciones matriciales
        A_np = np.array(A, dtype=float)
        b_np = np.array(B, dtype=float)
        c_np = np.array(C, dtype=float)

        # Calcular escala automaticamente segun la region factible del problema
        x_max, y_max = calcular_escala(A_np, b_np)

        # Crear los ejes con escala entera (sin decimales) y longitud fija de 6 unidades
        axes = Axes(
            x_range=[0, np.ceil(x_max), 1],
            y_range=[0, np.ceil(y_max), 1],
            x_length=6,
            y_length=6,
            axis_config={"include_numbers": True, "font_size": 18,
                         "decimal_number_config": {"num_decimal_places": 0}},
            tips=False,
        ).to_edge(LEFT, buff=0.7)

        # Agregar etiquetas a los ejes y dibujarlos en pantalla
        labels = axes.get_axis_labels(x_label="x_1", y_label="x_2")
        self.play(Create(axes), Write(labels))

        # Mostrar la funcion objetivo en la esquina superior derecha
        # Se construye el string de coeficientes dinamicamente segun cuantas variables haya
        coef_str = " + ".join([f"{C[i]:.0f}x_{i+1}" for i in range(len(C))])
        obj_text = MathTex(
            rf"\max \; z = {coef_str}",
            font_size=32,
            color=WHITE,
        ).to_corner(UR, buff=0.4)
        self.play(Write(obj_text))

        # Dibujar cada restriccion como una recta en el plano
        # y construir la leyenda con su color y etiqueta correspondiente
        colors_restricciones = [BLUE, ORANGE, PURPLE, TEAL]
        legend_items = []

        for i, (row, bi) in enumerate(zip(A_np, b_np)):
            a1, a2 = row

            # Ciclar los colores si hay mas restricciones que colores definidos
            color = colors_restricciones[i % len(colors_restricciones)]

            # Etiqueta con simbolo <= para indicar que es una desigualdad
            label_str = f"{int(a1)}x_1 + {int(a2)}x_2 \\leq {int(bi)}"

            if a2 != 0:
                # Caso general: despejar x2 de la restriccion para graficar
                # El max(..., 0) evita graficar valores negativos de y
                # que quedarian fuera del cuadrante visible
                def make_func(a1=a1, a2=a2, bi=bi):
                    return lambda x: max((bi - a1 * x) / a2, 0)
                func = make_func()

                # Graficar desde x=0 hasta x_max en todo el dominio visible
                # El recorte en y<0 lo hace la funcion directamente
                graph = axes.plot(func, x_range=[0, x_max],
                                  color=color, stroke_width=2)
            else:
                # Caso especial: a2 == 0 significa que la restriccion es vertical (x1 = cte)
                x_val = bi / a1
                p1 = axes.c2p(x_val, 0)
                p2 = axes.c2p(x_val, y_max)
                graph = Line(p1, p2, color=color, stroke_width=2)

            self.play(Create(graph), run_time=0.8)

            # Construir fila de la leyenda: punto de color + etiqueta LaTeX
            legend_dot = Dot(color=color, radius=0.07)
            legend_label = MathTex(label_str, font_size=20, color=color)
            legend_row = VGroup(legend_dot, legend_label).arrange(RIGHT, buff=0.15)
            legend_items.append(legend_row)

        # Agrupar todos los items de la leyenda y colocarlos en la esquina
        # Se usa buff=1.5 para que no tape la funcion objetivo que esta arriba
        legend = VGroup(*legend_items).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend.to_corner(UR, buff=1.5)
        self.play(FadeIn(legend))

        # Calcular y dibujar la region factible inicial (antes de cualquier iteracion)
        vertices_ini = calcular_vertices(A_np, b_np)
        region = None   # se inicializa en None por si no hay suficientes vertices

        if len(vertices_ini) > 2:
            poly_pts = [axes.c2p(v[0], v[1]) for v in vertices_ini]
            region = Polygon(*poly_pts, fill_color=YELLOW, fill_opacity=0.3,
                             stroke_color=YELLOW, stroke_width=1.5)
            self.play(FadeIn(region))

        # Etiqueta de iteracion en la esquina inferior derecha
        iter_label = Text("Iteracion: 0", font_size=24).to_corner(DR, buff=0.5)
        self.play(Write(iter_label))

        # Punto rojo que representa la solucion actual del simplex
        # Comienza en el origen (0, 0)
        dot = Dot(axes.c2p(points[0][0], points[0][1]), color=RED, radius=0.12)
        self.play(FadeIn(dot))

        # Variable para rastrear la recta objetivo del frame anterior
        # y poder hacer Transform en lugar de crear una nueva cada vez
        obj_line = None

        # ==========================================
        # Loop principal: animar cada iteracion del simplex
        # ==========================================
        for idx in range(len(points)):
            x_val, y_val = float(points[idx][0]), float(points[idx][1])

            # Calcular el valor de z en este punto, redondeado a 2 decimales
            z = round(c_np[0] * x_val + c_np[1] * y_val, 2)

            # Actualizar etiqueta con numero de iteracion y z actual
            new_label = Text(f"Iteracion: {idx}   z = {z:.2f}", font_size=24).to_corner(DR, buff=0.5)

            # Actualizar la funcion objetivo en pantalla mostrando el z actual
            # Se coloca en UR para que coincida con donde estaba al inicio
            new_obj_text = MathTex(
                rf"\max \; z = {coef_str} = {z:.2f}",
                font_size=32,
                color=WHITE,
            ).to_corner(UR, buff=0.4)

            # Animar ambos cambios al mismo tiempo para que se vea mas fluido
            self.play(
                Transform(iter_label, new_label),
                Transform(obj_text, new_obj_text),
                run_time=0.3
            )

            # Mover el punto rojo al vertice actual
            new_dot_pos = axes.c2p(x_val, y_val)
            self.play(dot.animate.move_to(new_dot_pos), run_time=0.8)

            # Dibujar la trayectoria entre el vertice anterior y el actual
            if idx > 0:
                prev = points[idx - 1]
                line = Line(
                    axes.c2p(float(prev[0]), float(prev[1])),
                    axes.c2p(x_val, y_val),
                    color=RED,
                    stroke_width=2,
                )
                self.play(Create(line), run_time=0.4)

            # Actualizar la region factible visible agregando el corte c·x >= z
            # Esto muestra graficamente que la region de mejora se va reduciendo
            # No se actualiza en la ultima iteracion porque ya es el optimo
            if region is not None and idx > 0 and idx < (len(points) - 1):

                # La restriccion c·x >= z se reescribe como -c·x <= -z
                # para que tenga la misma forma que las restricciones originales
                a_extra = np.array([[-c_np[0], -c_np[1]]])
                b_extra = np.array([-z])

                # Recalcular los vertices con la restriccion adicional
                vertices_nuevos = calcular_vertices(
                    A_np, b_np,
                    restricciones_extra=[(a_extra, b_extra)]
                )

                if len(vertices_nuevos) > 2:
                    poly_pts_new = [axes.c2p(v[0], v[1]) for v in vertices_nuevos]

                    # El color de la region cambia de amarillo a verde conforme avanza
                    # progreso va de 0 a 1 segun en que iteracion estemos
                    progreso = idx / max(len(points) - 1, 1)
                    color_nuevo = interpolate_color(YELLOW, GREEN, progreso)

                    nueva_region = Polygon(
                        *poly_pts_new,
                        fill_color=color_nuevo,
                        fill_opacity=0.35,
                        stroke_color=color_nuevo,
                        stroke_width=1.5,
                    )
                    # Transform anima el cambio de forma del poligono suavemente
                    self.play(Transform(region, nueva_region), run_time=0.6)

            # Dibujar la recta objetivo z = c·x en el valor actual
            # Esta recta se mueve en cada iteracion mostrando el avance
            if c_np[1] != 0:
                # Caso general: despejar x2 de z = c1*x1 + c2*x2
                def make_obj(z=z, c_np=c_np):
                    return lambda x: (z - c_np[0] * x) / c_np[1]
                obj_func = make_obj()

                # Limitar el rango de graficacion al dominio visible
                x_end = min(z / c_np[0], x_max) if c_np[0] > 0 else x_max
                new_obj_line = axes.plot(obj_func, x_range=[0, x_end],
                                         color=GREEN, stroke_width=2.5)
            else:
                # Caso especial: c2 == 0, la recta objetivo es vertical
                x_line = z / c_np[0]
                p1 = axes.c2p(x_line, 0)
                p2 = axes.c2p(x_line, y_max)
                new_obj_line = Line(p1, p2, color=GREEN, stroke_width=2.5)

            # Primera iteracion: crear la recta. Iteraciones siguientes: transformar
            if obj_line is None:
                self.play(Create(new_obj_line), run_time=0.5)
            else:
                self.play(Transform(obj_line, new_obj_line), run_time=0.5)

            obj_line = new_obj_line
            self.wait(0.5)

            # En la ultima iteracion, agrandar y cambiar el color del punto a verde
            # para indicar visualmente que se llego al optimo
            if idx == len(points) - 1:
                self.play(dot.animate.set_color(GREEN).scale(1.5))

        # Mostrar la solucion optima al final de la animacion
        result_text = MathTex(
            rf"\text{{Optimo: }} x_1={sol[0]:.2f},\; x_2={sol[1]:.2f},\; z={z_opt:.2f}",
            font_size=28,
            color=YELLOW,
        ).to_edge(DOWN, buff=0.3)

        self.play(Write(result_text))

        # Esperar 7 segundos antes de cerrar para que el usuario pueda leer el resultado
        self.wait(7)
