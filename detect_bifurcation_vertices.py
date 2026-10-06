import numpy as np
from geometry import project_on_branches
def detect_bifurcation_vertices(vertices, branches, cylinders, branch_ids, xis, faces, threshold=4.0):
    bifurcation_vertices = []

    for i, v in enumerate(vertices):

        # Distancia a la rama asignada
        result = project_on_branches(v, branches)

        if result is None:
            continue

        branch, xi, p, vec, d = result

        # Condición 1: zona distal
        cond2 = xis[i] > 0.85

        # Condición 2: triángulos mezclan ramas
        caras = np.where(faces == i)[0]
        mezcla = False
        for cara in caras:
            v0, v1, v2 = faces[cara]
            ramas = {branch_ids[v0], branch_ids[v1], branch_ids[v2]}
            if len(ramas) > 1:
              print(
                  "Cara mezcla ramas:",
                   branch_ids[v0],
                   branch_ids[v1],
                   branch_ids[v2],
                   " -> vértices:", v0, v1, v2
              )
            #if len(set([branch_ids[v0], branch_ids[v1], branch_ids[v2]])) > 1:
              mezcla = True
               ## print("triángulos mezclan rama", v0, v1, v2)
              break

        # Condición 3: distancia grande (opcional)
        cond1 = d > threshold

        if cond1 and cond2 and mezcla:
            bifurcation_vertices.append(i)

    return bifurcation_vertices
