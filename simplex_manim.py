import numpy as np
from manim import *

# =====================================
# SIMPLEX 
# =====================================

def simplex_max(A, b, c):
    A = np.array(A, dtype=float)
    b = np.array(b, dtype=float)
    c = np.array(c, dtype=float)

    m, n = A.shape

    tableau = np.zeros((m + 1, n + m + 1))
    tableau[:m, :n] = A
    tableau[:m, n:n + m] = np.eye(m)
    tableau[:m, -1] = b
    tableau[-1, :n] = -c

    var_names = [f"x{i+1}" for i in range(n)] + [f"s{i+1}" for i in range(m)]
    basic_vars = [f"s{i+1}" for i in range(m)]

    points = []
    points.append(np.zeros(n))

    while True:
        z_row = tableau[-1, :-1]
        entering_col = np.argmin(z_row)

        if z_row[entering_col] >= 0:
            break

        ratios = []
        for i in range(m):
            col_val = tableau[i, entering_col]
            if col_val > 0:
                ratios.append(tableau[i, -1] / col_val)
            else:
                ratios.append(np.inf)

        leaving_row = np.argmin(ratios)

        if ratios[leaving_row] == np.inf:
            raise ValueError("Problema no acotado")

        basic_vars[leaving_row] = var_names[entering_col]

        pivot = tableau[leaving_row, entering_col]
        tableau[leaving_row, :] /= pivot

        for i in range(m + 1):
            if i != leaving_row:
                tableau[i, :] -= tableau[i, entering_col] * tableau[leaving_row, :]

        current_solution = np.zeros(n)
        for i in range(m):
            var = basic_vars[i]
            if var.startswith("x"):
                idx = int(var[1:]) - 1
                current_solution[idx] = tableau[i, -1]

        points.append(current_solution.copy())

    solution = np.zeros(n)
    for i in range(m):
        var = basic_vars[i]
        if var.startswith("x"):
            idx = int(var[1:]) - 1
            solution[idx] = tableau[i, -1]

    optimal_value = tableau[-1, -1]

    return solution, optimal_value, tableau, points


# =====================================
# FUNCION: calcular vertices de la region factible
# =====================================

def calcular_vertices(A_np, b_np, restricciones_extra=None):
    if restricciones_extra:
        A_total = np.vstack([A_np] + [r[0] for r in restricciones_extra])
        b_total = np.concatenate([b_np] + [r[1] for r in restricciones_extra])
    else:
        A_total = A_np
        b_total = b_np

    m = len(A_total)
    vertices = []

    for i in range(m):
        for j in range(i + 1, m):
            A_sub = np.array([A_total[i], A_total[j]])
            b_sub = np.array([b_total[i], b_total[j]])
            if abs(np.linalg.det(A_sub)) > 1e-10:
                sol_v = np.linalg.solve(A_sub, b_sub)
                if np.all(sol_v >= -1e-6) and np.all(A_total @ sol_v <= b_total + 1e-6):
                    vertices.append(np.round(sol_v, 2))

    for i in range(m):
        a1, a2 = A_total[i, 0], A_total[i, 1]
        bi = b_total[i]
        if a1 > 1e-10:
            p = np.array([bi / a1, 0.0])
            if np.all(A_total @ p <= b_total + 1e-6):
                vertices.append(np.round(p, 2))
        if a2 > 1e-10:
            p = np.array([0.0, bi / a2])
            if np.all(A_total @ p <= b_total + 1e-6):
                vertices.append(np.round(p, 2))

    # Intersecciones de restricciones extra con los ejes
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
    
    origen = np.array([0.0, 0.0])
    if np.all(A_total @ origen <= b_total + 1e-6):
        vertices.append(origen)

    if len(vertices) == 0:
        return np.array([]).reshape(0, 2)

    vertices = np.unique(np.round(vertices, 6), axis=0)

    if len(vertices) > 2:
        center = np.mean(vertices, axis=0)
        angles = np.arctan2(vertices[:, 1] - center[1], vertices[:, 0] - center[0])
        vertices = vertices[np.argsort(angles)]

    return vertices


# =====================================
# FUNCION: calcular escala apropiada
# =====================================

def calcular_escala(A_np, b_np, margen=1.3):
    vertices = calcular_vertices(A_np, b_np)

    if len(vertices) == 0:
        escala = float(max(b_np) * margen)
        return escala, escala

    x_max_real = float(np.max(vertices[:, 0]))
    y_max_real = float(np.max(vertices[:, 1]))

    x_max = max(x_max_real * margen, 1.0)
    y_max = max(y_max_real * margen, 1.0)

    escala_uniforme = max(x_max, y_max)

    return escala_uniforme, escala_uniforme


# =====================================
# ESCENA MANIM
# =====================================

class SimplexScene(Scene):
    # C, A, B son inyectados desde el programa principal
    # antes de llamar a render()
    C = []
    A = []
    B = []

    def construct(self):
        C = self.__class__.C
        A = self.__class__.A
        B = self.__class__.B

        sol, z_opt, tab, points = simplex_max(A, B, C)

        A_np = np.array(A, dtype=float)
        b_np = np.array(B, dtype=float)
        c_np = np.array(C, dtype=float)

        x_max, y_max = calcular_escala(A_np, b_np)

        axes = Axes(
            x_range=[0, np.ceil(x_max), 1],
            y_range=[0, np.ceil(y_max), 1],
            x_length=6,
            y_length=6,
            axis_config={"include_numbers": True, "font_size": 18,
                         "decimal_number_config": {"num_decimal_places": 2}},
            tips=False,
        ).to_edge(LEFT, buff=0.7)


        #La sección anterior creó las escalas para el plano cartesiano

        # Función objetivo prominente en esquina superior izquierda
        coef_str = " + ".join([f"{C[i]:.0f}x_{i+1}" for i in range(len(C))])
        obj_text = MathTex(
            rf"\max \; z = {coef_str}",
            font_size=32,
            color=WHITE,
        ).to_corner(UR, buff=0.4)
        self.play(Write(obj_text))

        # Restricciones y leyenda
        colors_restricciones = [BLUE, ORANGE, PURPLE, TEAL]
        legend_items = []

        for i, (row, bi) in enumerate(zip(A_np, b_np)):
            a1, a2 = row
            color = colors_restricciones[i % len(colors_restricciones)]
            label_str = f"{int(a1)}x_1 + {int(a2)}x_2 \\leq {int(bi)}"

            if a2 != 0:
                def make_func(a1=a1, a2=a2, bi=bi):
                    return lambda x: (bi - a1 * x) / a2
                func = make_func()
                graph = axes.plot(func, x_range=[0, bi / a1 if a1 > 0 else x_max],
                                  color=color, stroke_width=2)
            else:
                x_val = bi / a1
                p1 = axes.c2p(x_val, 0)
                p2 = axes.c2p(x_val, y_max)
                graph = Line(p1, p2, color=color, stroke_width=2)

            self.play(Create(graph), run_time=0.8)

            legend_dot = Dot(color=color, radius=0.07)
            legend_label = MathTex(label_str, font_size=20, color=color)
            legend_row = VGroup(legend_dot, legend_label).arrange(RIGHT, buff=0.15)
            legend_items.append(legend_row)

        legend = VGroup(*legend_items).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        legend.to_corner(UR, buff=1.5)
        self.play(FadeIn(legend))

        # Region factible inicial
        vertices_ini = calcular_vertices(A_np, b_np)
        region = None

        if len(vertices_ini) > 2:
            poly_pts = [axes.c2p(v[0], v[1]) for v in vertices_ini]
            region = Polygon(*poly_pts, fill_color=YELLOW, fill_opacity=0.3,
                             stroke_color=YELLOW, stroke_width=1.5)
            self.play(FadeIn(region))

        iter_label = Text("Iteracion: 0", font_size=24).to_corner(DR, buff=0.5)
        self.play(Write(iter_label))

        dot = Dot(axes.c2p(points[0][0], points[0][1]), color=RED, radius=0.12)
        self.play(FadeIn(dot))

        obj_line = None

        for idx in range(len(points)):
            x_val, y_val = float(points[idx][0]), float(points[idx][1])
            z = round(c_np[0] * x_val + c_np[1] * y_val, 2)

            new_label = Text(f"Iteracion: {idx}   z = {z:.2f}", font_size=24).to_corner(DR, buff=0.5)

            # Actualizar función objetivo mostrando el z actual
            new_obj_text = MathTex(
                rf"\max \; z = {coef_str} = {z:.2f}",
                font_size=32,
                color=WHITE,
            ).to_corner(UL, buff=0.4)

            self.play(
                Transform(iter_label, new_label),
                Transform(obj_text, new_obj_text),
                run_time=0.3
            )

            new_dot_pos = axes.c2p(x_val, y_val)
            self.play(dot.animate.move_to(new_dot_pos), run_time=0.8)

            if idx > 0:
                prev = points[idx - 1]
                line = Line(
                    axes.c2p(float(prev[0]), float(prev[1])),
                    axes.c2p(x_val, y_val),
                    color=RED,
                    stroke_width=2,
                )
                self.play(Create(line), run_time=0.4)

            # Actualizar region factible cortada por c·x >= z
            if region is not None and idx > 0 and idx < (len(points) - 1):
                a_extra = np.array([[-c_np[0], -c_np[1]]])
                b_extra = np.array([-z])

                vertices_nuevos = calcular_vertices(
                    A_np, b_np,
                    restricciones_extra=[(a_extra, b_extra)]
                )

                if len(vertices_nuevos) > 2:
                    poly_pts_new = [axes.c2p(v[0], v[1]) for v in vertices_nuevos]
                    progreso = idx / max(len(points) - 1, 1)
                    color_nuevo = interpolate_color(YELLOW, GREEN, progreso)
                    nueva_region = Polygon(
                        *poly_pts_new,
                        fill_color=color_nuevo,
                        fill_opacity=0.35,
                        stroke_color=color_nuevo,
                        stroke_width=1.5,
                    )
                    self.play(Transform(region, nueva_region), run_time=0.6)

            # Recta objetivo dinámica
            if c_np[1] != 0:
                def make_obj(z=z, c_np=c_np):
                    return lambda x: (z - c_np[0] * x) / c_np[1]
                obj_func = make_obj()
                x_end = min(z / c_np[0], x_max) if c_np[0] > 0 else x_max
                new_obj_line = axes.plot(obj_func, x_range=[0, x_end],
                                         color=GREEN, stroke_width=2.5)
            else:
                x_line = z / c_np[0]
                p1 = axes.c2p(x_line, 0)
                p2 = axes.c2p(x_line, y_max)
                new_obj_line = Line(p1, p2, color=GREEN, stroke_width=2.5)

            if obj_line is None:
                self.play(Create(new_obj_line), run_time=0.5)
            else:
                self.play(Transform(obj_line, new_obj_line), run_time=0.5)

            obj_line = new_obj_line
            self.wait(0.5)

            if idx == len(points) - 1:
                self.play(dot.animate.set_color(GREEN).scale(1.5))

        # Resultado final
        result_text = MathTex(
            rf"\text{{Optimo: }} x_1={sol[0]:.2f},\; x_2={sol[1]:.2f},\; z={z_opt:.2f}",
            font_size=28,
            color=YELLOW,
        ).to_edge(DOWN, buff=0.3)

        self.play(Write(result_text))
        self.wait(7)
