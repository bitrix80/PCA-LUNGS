"""


Transformació dels punts de la STL cap als cilindres.

Implementa

x
 ↓
argmin ||x-lambda(xi)||

↓

xi

↓

v=x-lambda(xi)

↓

phi_cil(xi)

↓

phi_cil(xi)+v/||v||

"""

import numpy as np
import vtk

from geometry import (
    project_on_branches,
)

from cylinder import (
    map_point_to_cylinder,
)
from export_seed_faces import export_seed_faces


# ============================================================
# Transformar UN punt al cilindre
# ============================================================

def map_single_point(x,
                     branches,
                     cylinders):
    """
    Transforma un únic punt.
    """

    result = project_on_branches(
        x,
        branches
    )

    if result is None:
        return None

    branch, xi, p, v, d = result

    return map_point_to_cylinder(
        branch,
        xi,
        v,
        branches,
        cylinders
    )


# ============================================================
# Transformar tots els punts
# ============================================================

def map_points(points,
               branches,
               cylinders):
    """
    Parameters
    ----------
    points : (N,3)

    Returns
    -------
    transformed_points
    """

    new_points = np.zeros_like(points)

    for i in range(len(points)):

        new_points[i] = map_single_point(
            points[i],
            branches,
            cylinders
        )

    return new_points


# ============================================================
# Transformació amb informació extra
# ============================================================

def map_points_verbose(points,
                       branches,
                       cylinders):
    """
    Igual que map_points però
    també retorna

    xi

    branca

    distància

    vector de projecció
    """

    N = len(points)

    new_points = np.zeros_like(points)

    xis = np.zeros(N)

    branch_ids = np.zeros(N, dtype=int)

    distances = np.zeros(N)

    projection_vectors = np.zeros((N,3))

    for i in range(N):

        result = project_on_branches(
            points[i],
            branches
        )

        if result is None:
            continue

        branch, xi, p, v, d = result

        # cylinders es un diccionario {id: CylinderBranch}
        cylinders_list = list(cylinders.values())
        
        new_points[i] = map_point_to_cylinder(
            branch,
            xi,
            v,
            branches,
            cylinders_list
        )

        xis[i] = xi

        branch_ids[i] = branch["id"]

        distances[i] = d

        projection_vectors[i] = v

    return (
        new_points,
        xis,
        branch_ids,
        distances,
        projection_vectors
    )


# ============================================================
# Transformació in-place
# ============================================================

def map_mesh_vertices(vertices,
                      branches,
                      cylinders,
                      faces):

    # Comencem amb la malla original
    new_vertices = vertices.copy()
    # 1. Asignación original
    distancies = np.full(len(vertices), np.nan)
    xis = np.full(len(vertices), np.nan)
    xis_centerline = np.full(len(vertices), np.nan)
    xis_cilindro   = np.full(len(vertices), np.nan)   # xi que usa el cilindro
    branch_ids = np.full(len(vertices), -1, dtype=int)
    projection_vectors = np.zeros((len(vertices), 3))

     # === 1. Asignación original de branch, xi y proyección ===
    for i, x in enumerate(vertices):

        result = project_on_branches(x, branches)
        if result is None:
            continue

        branch, xi_centerline, p, v, d = result

        # OJO Calcular xi del cilindro SIEMPRE
        #if branch["id"] != branches[0]["id"]:
        #    xi = 1.0 - xi_centerline   # invertido en hijas
            #xi = xi_centerline
        #else:
            #xi = xi_centerline         # tal cual en la tráquea
        #    xi = 1.0 - xi_centerline 
        xi = xi_centerline # OJOOO no invierto los hijos


        distancies[i] = d
        xis_centerline[i] = xi_centerline
        xis_cilindro[i]   = xi
            
        branch_ids[i] = branch["id"]
        

        # xi original
        #xi_original = xi

        # Invertir xi en ramas hijas
        #if branch["id"] != branches[0]["id"]:
        #    xi = 1.0 - xi_original

        branch_ids[i]       = branch["id"]
        projection_vectors[i] = v

        new_vertices[i] = map_point_to_cylinder(
            branch,
            xi,
            v,
            branches,
            cylinders
        )

    return (
        new_vertices,
        distancies,
        xis_centerline,
        xis_cilindro,
        branch_ids,
        projection_vectors      # <-- AFEGEIX AIX?~R
    )
    # === 3. CORRECCIÓN POR PROXIMIDAD LOCAL ===

    #root = branches[0]
    #bif = root["points"][-1]
    #R = 12.0   # ajusta según tu escala

    #for i, v in enumerate(vertices):
    #    if np.linalg.norm(v - bif) < R:
    #        branch_ids[i] = root["id"]
    #        xis[i] = 1.0
    #        new_vertices[i] = map_point_to_cylinder(
    #            root, 1.0, projection_vectors[i], branches, cylinders
    #        )

    # Umbral de proximidad entre vértices de una cara
    #PROX = 4.0   # ajusta según tu escala

    #for cara in faces:
    #    v0, v1, v2 = cara

    #    p0 = vertices[v0]
    #    p1 = vertices[v1]
    #    p2 = vertices[v2]

        # Distancias entre los vértices de la cara
    #    d01 = np.linalg.norm(p0 - p1)
    #    d12 = np.linalg.norm(p1 - p2)
    #    d20 = np.linalg.norm(p2 - p0)

        # Si los tres vértices están cerca entre sí
    #    if d01 < PROX and d12 < PROX and d20 < PROX:

            # Reasignar los 3 vértices a la raíz
    #        branch_ids[v0] = root_id
    #        branch_ids[v1] = root_id
    #        branch_ids[v2] = root_id

    #        xis[v0] = 1.0
    #        xis[v1] = 1.0
    #        xis[v2] = 1.0

            # Recalcular proyección
    #        new_vertices[v0] = map_point_to_cylinder(root, 1.0, projection_vectors[v0], branches, cylinders)
    #        new_vertices[v1] = map_point_to_cylinder(root, 1.0, projection_vectors[v1], branches, cylinders)
    #        new_vertices[v2] = map_point_to_cylinder(root, 1.0, projection_vectors[v2], branches, cylinders)


    #bif = root["points"][-1]   # punto de bifurcación de la rama raíz
    #R = 12.0                    # ajusta según escala

    #for i, v in enumerate(vertices):
    #    if np.linalg.norm(v - bif) < R:
    #        branch_ids[i] = root["id"]
    #        xis[i] = 1.0
    #         # Recalcular la proyección con la rama raíz
    #        projection_vectors[i] = projection_vectors[i]  # se mantiene
    #        new_vertices[i] = map_point_to_cylinder(
    #            root,
    #            1.0,
    #            projection_vectors[i],
    #            branches,
    #            cylinders
    #        )
    # === 3. CORRECCIÓN POR CARA: si una cara mezcla ramas, forzar raíz ===

    #root = branches[0]          # la raíz
    #root_id = root["id"]

   # for cara in faces:
   #     v0, v1, v2 = cara

   #     ramas = {branch_ids[v0], branch_ids[v1], branch_ids[v2]}

        # Si mezcla ramas, reasignar los 3 vértices a la raíz
   #     if len(ramas) > 1:
   #         branch_ids[v0] = root_id
   #         branch_ids[v1] = root_id
   #         branch_ids[v2] = root_id

   #         xis[v0] = 1.0
   #         xis[v1] = 1.0
   #         xis[v2] = 1.0

   #         # Recalcular proyección para cada vértice
   #         new_vertices[v0] = map_point_to_cylinder(
   #             root, 1.0, projection_vectors[v0], branches, cylinders
   #         )
   #         new_vertices[v1] = map_point_to_cylinder(
   #             root, 1.0, projection_vectors[v1], branches, cylinders
   #         )
   #         new_vertices[v2] = map_point_to_cylinder(
   #             root, 1.0, projection_vectors[v2], branches, cylinders
   #     )



#Camp vectors projectors sobre la malla original

def compute_projection_vectors(vertices,
                               branches,
                               cylinders_by_id,
                               R=1.0):
    """
    Calcula el vector de projecció v = x - lambda(xi)
    per a cada vèrtex de la malla original.
    """
    projection_vectors = []
    mapped_points = []
    xis_list = []
    branch_ids_list = []
    
    for x in vertices:
        result = project_on_branches(
            x,
            branches
        )

        if result is None:
            projection_vectors.append(np.zeros(3))
            mapped_points.append(np.zeros(3))
            xis_list.append(0.0)
            branch_ids_list.append(-1)
            continue

        branch, xi, p, v, d = result
        projection_vectors.append(v)
        xis_list.append(xi)
        branch_ids_list.append(branch["id"])
        cyl = cylinders_by_id[branch["id"]]
                
        # punto sobre el eje del cilindro template
        lambda_template = cyl.origin + xi * cyl.length * cyl.direction

        # vector radial reescalado
        v_template = v / np.linalg.norm(v) * R

        # punto final del mapping
        mapped_point = lambda_template + v_template

        mapped_points.append(mapped_point)

   # projection_vectors = np.asarray(projection_vectors)
    #magnitudes = np.linalg.norm(projection_vectors, axis=1)
    #mapped_points = np.asarray(mapped_points)
    #print("Nombre vectors no nuls:",
    #      np.sum(magnitudes > 1e-8))
    #print("Magnitud màxima:",
    #      magnitudes.max())
    #print("Magnituds >4:",
    #      np.sum(magnitudes > 4))
    return (np.asarray(projection_vectors),
            np.asarray(mapped_points),
            np.asarray(xis_list),
            np.asarray(branch_ids_list))
    print(mapped_points.shape)
    print(mapped_points[:10])


def build_face_neighbors(faces):
    """
    Construye la lista de vecinos por cara.
    faces: array Nx3 con índices de vértices
    """
    from collections import defaultdict

    # mapa: arista -> lista de caras que la contienen
    edge_to_faces = defaultdict(list)

    for fi, face in enumerate(faces):
        v0, v1, v2 = face

        edges = [
            tuple(sorted((v0, v1))),
            tuple(sorted((v1, v2))),
            tuple(sorted((v2, v0)))
        ]

        for e in edges:
            edge_to_faces[e].append(fi)

    # ahora construimos vecinos
    face_neighbors = [[] for _ in range(len(faces))]

    for e, flist in edge_to_faces.items():
        if len(flist) > 1:
            for f in flist:
                for g in flist:
                    if f != g:
                        face_neighbors[f].append(g)

    # eliminar duplicados
    face_neighbors = [list(set(neighs)) for neighs in face_neighbors]

    return face_neighbors
def assign_branch_by_faces(faces,
                           vertices,
                           branch_ids_list,
                           face_neighbors,
                           id_trachea,
                           branches, 
                           distances,
                           xis_centerline):
    """
    Asigna branch_id por elementos (caras) y lo propaga recursivamente
    desde las caras de la tráquea.
    """

    n_faces = len(faces)

    # --- Paso 1: branch_id por cara (inicialmente por mayoría)
    face_branch_id = np.zeros(n_faces, dtype=int)
    n_vertices = len(vertices)
    vertex_branch_id = np.array(branch_ids_list, dtype=int)
    
    for i, face in enumerate(faces):
        bids = [branch_ids_list[v] for v in face]
        face_branch_id[i] = max(set(bids), key=bids.count)

    # --- Paso 2: caras semilla de la tráquea (mayoría tráquea)
   # seed_faces = [i for i in range(n_faces) if face_branch_id[i] == id_trachea]
    # distancia de cada vértice al origen
    dist_to_origin = branches[0]["points"][0]
    # umbral automático: 10% de las distancias más pequeñas
    R0 = np.percentile(distances, 10)
    seed_faces = [
        i for i, face in enumerate(faces)
        if np.mean([np.linalg.norm(vertices[v]-dist_to_origin) for v in face]) < R0
    ]
    print("Seed faces:", seed_faces[:20])
    export_seed_faces(vertices, faces, seed_faces, "seed_faces.vtp")
    export_face_branch_id(
        faces,
        [1 if i in seed_faces else 0 for i in range(n_faces)],
        vertices,
        "debug_seed_faces.vtp"
    )
    print("acabo el export seed faces")

    # --- Paso 3: flood fill
    queue = list(seed_faces)
    visited = set(seed_faces)

    #trachea_cl = np.array(branches[0]["points"])
    #child_cls = [np.array(b["points"]) for b in branches[1:]]
    #epsilon = 0.2 * np.median(distances)
    print("Entro al flood fill")
    print("branches[0]['id'] =", branches[0]["id"])
    print("id_trachea:", id_trachea)
    print("ids únicos en face_branch_id (inicial):", set(face_branch_id))
    while queue:
        f = queue.pop(0)
        parent_bid = face_branch_id[f]   # rama padre
        for neigh in face_neighbors[f]:
            neigh = int(neigh)
            if neigh in visited:
                continue
            #rama origen del vecino
            neigh_bid = face_branch_id[neigh]
            #print("rama origen vecino",neigh_bid)
            #print("id_traquea",id_trachea)
            propagated = False
             # --- REGLA JERÁRQUICA ---
            if parent_bid == id_trachea:
                # La tráquea puede propagar a cualquier bronquio
                # pero NO puede cambiar un bronquio por otro
                # (si ya es bronquio L, no lo convierto en R)
                face_branch_id[neigh] = id_trachea
                propagated = True
                #print("parent_bid == id_trachea",neigh_bid)
            else:
                # El padre es un bronquio (L o R)
                # Solo permito que el vecino herede ESA MISMA rama
                if neigh_bid == id_trachea:
                    # Si el vecino era tráquea, lo convierto en el bronquio del padre
                    face_branch_id[neigh] = parent_bid
                    propagated = True
                    print("vecino era tráque-->bronquio del padre",neigh_bid)
                elif neigh_bid == parent_bid:
                    # Si ya es el mismo bronquio, lo dejo igual
                    propagated = True
                    #face_branch_id[neigh] = parent_bid
                    print("Si ya es el mismo bronquio, lo dejo igual",neigh_bid)
                else:
                    # Si es el otro bronquio --> NO lo toco
                    continue
            if propagated:
                visited.add(neigh)
                queue.append(neigh)
                for v in faces[neigh]:
                    vertex_branch_id[v] = face_branch_id[neigh] 

    print("unique vertex_branch_id final:", set(vertex_branch_id)) 
    return vertex_branch_id


def export_face_branch_id(faces, face_branch_id, vertices, filename="face_branch_id.vtp"):
    poly = vtk.vtkPolyData()

    # puntos ficticios (uno por cara)
    vtk_points = vtk.vtkPoints()
    for i, face in enumerate(faces):
        # centroide de la cara
        v0, v1, v2 = vertices[face]
        centroid = (v0 + v1 + v2) / 3.0
        vtk_points.InsertNextPoint(*centroid)

    poly.SetPoints(vtk_points)

    # una celda por cara
    cells = vtk.vtkCellArray()
    for i in range(len(faces)):
        cells.InsertNextCell(1)
        cells.InsertCellPoint(i)

    poly.SetVerts(cells)

    # branch_id por cara
    arr = vtk.vtkIntArray()
    arr.SetName("face_branch_id")
    for bid in face_branch_id:
        arr.InsertNextValue(int(bid))

    poly.GetPointData().AddArray(arr)

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()

def distance_to_centerline(point, centerline_points):
    """
    Distancia mínima de 'point' a una polyline dada por centerline_points (array Mx3).
    """
    dmin = np.inf
    for i in range(len(centerline_points) - 1):
        p0 = centerline_points[i]
        p1 = centerline_points[i + 1]
        v = p1 - p0
        w = point - p0
        t = np.dot(w, v) / np.dot(v, v)
        t = max(0.0, min(1.0, t))
        proj = p0 + t * v
        d = np.linalg.norm(point - proj)
        if d < dmin:
            dmin = d
    return dmin
def map_faces_to_cylinders(vertices,
                           faces,
                           face_branch_id,
                           branches,
                           cylinders_by_id):
    """
    Proyecta la geometría sintética cara-a-cara usando la rama correcta.
    Evita caras mezcladas.
    """
    # Diccionario ID --->branch
    branches_by_id = { b["id"]: b for b in branches }
    # cylinders es un diccionario {id: CylinderBranch}
    cylinders_list = list(cylinders_by_id.values())

    # nueva geometría proyectada
    new_vertices = np.zeros_like(vertices)

    # Para evitar reproyectar vértices repetidos
    projected = np.zeros(len(vertices), dtype=bool)
    # SOLO iteramos sobre las caras que sí tienen branch_id
    for f_id in range(len(face_branch_id)):
        face = faces[f_id]
        # rama correcta para esta cara
        bid = face_branch_id[f_id]
        branch = branches_by_id[bid]
        cylinder = cylinders_by_id[bid]   # objeto CylinderBranch

        # proyectar los 3 vértices de la cara usando ESTA rama
        for v_id in face:

            if projected[v_id]:
                continue

            # proyectar el vértice sobre la centerline de la rama
            result_assigned = project_on_branches(vertices[v_id], [branch])
            if result_assigned is None:
                continue

            _, xi_assigned, _, vproj_assigned, d_assigned = result_assigned

            d_others = []
            for other_bid, other_branch in branches_by_id.items():
                if other_bid == bid:
                    continue
                res_other = project_on_branches(vertices[v_id], [other_branch])
                if res_other is not None:
                    _, _, _, _, d_other = res_other
                    d_others.append(d_other)

            if len(d_others) == 0:
                d_min_other = 1e9
            else:
                d_min_other = min(d_others)
            
            
            # --- 3. Detectar ambigüedad geométrica ---
            # epsilon = umbral de ambigüedad
            epsilon = 0.2 * np.median([
                np.linalg.norm(vertices[f[0]] - vertices[f[1]])
                for f in faces
            ])

            if abs(d_assigned - d_min_other) < epsilon:
    # Cara ambigua → proyectar igualmente, pero con la rama asignada
    # (porque tú quieres SIEMPRE cilindro sintético)
                # mapear al cilindro correspondiente
                new_vertices[v_id] = map_point_to_cylinder(
                    branch,
                    xi_assigned,
                    vproj_assigned,
                    branches,
                    list(cylinders_by_id.values())
                )
            else:
                # Cara clara → proyectar normal
                new_vertices[v_id] = map_point_to_cylinder(
                    branch,
                    xi_assigned,
                    vproj_assigned,
                    branches,
                    list(cylinders_by_id.values())
                )
            projected[v_id] = True

    return new_vertices
