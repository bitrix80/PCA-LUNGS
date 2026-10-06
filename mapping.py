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
import sys
from debug_export_flood_fill import export_debug_step

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

    branch, xi, p, v, d , outside = result

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

        branch, xi, p, v, d , outside = result

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

        branch, xi_centerline, p, v, d, outside  = result
        # if i == 455 :
        #     print("en map_mesh_vertices",branch,xi_centerline,v)

        # OJO Calcular xi del cilindro SIEMPRE
        #if branch["id"] != branches[0]["id"]:
        #    xi = 1.0 - xi_centerline   # invertido en hijas
            #xi = xi_centerline
        #else:
            #xi = xi_centerline         # tal cual en la tráquea
        #    xi = 1.0 - xi_centerline 
        
        
        xi                    = xi_centerline # OJOOO no invierto los hijos
        distancies[i]         = d
        xis_centerline[i]     = xi_centerline
        xis_cilindro[i]       = xi
        branch_ids[i]         = branch["id"]
        projection_vectors[i] = v
                    

        # xi original
        #xi_original = xi

        # Invertir xi en ramas hijas
        #if branch["id"] != branches[0]["id"]:
        #    xi = 1.0 - xi_original


        new_vertices[i] = map_point_to_cylinder(
            branch,
            xi,
            v,
            branches,
            cylinders
        )
        if i == 455 :
            print("las coords-en map_mesh",new_vertices[i])

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

        branch, xi, p, v, d, outside  = result
        
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
    n_vertices = len(vertices)
    vertex_branch_id = np.array(branch_ids_list, dtype=int)

    id_not_assigned = -1
    vertex_update = vertex_branch_id.copy()
    vertex_update[:]=id_not_assigned

    # --- Paso 1: branch_id por cara (inicialmente por mayoría)
    face_branch_id = np.zeros(n_faces, dtype=int)

    for i, face in enumerate(faces):
        bids = [branch_ids_list[v] for v in face]
        face_branch_id[i] = max(set(bids), key=bids.count)
    # print("DEBUG: escrito debug_original_vertices_branch.vtp")
    
    # export_face_branch_id(
    #     faces,
    #     face_branch_id,
    #     vertices,
    #     "debug_original_face_branch.vtp"
    # )
    
    # f_debug = 7847  # mismo índice

    # print("face_branch_id[debug] (inicial):", face_branch_id[f_debug])
    # print("vertex_branch_id en vértices debug (inicial):",
    #         vertex_branch_id[faces[f_debug][0]],
    #         vertex_branch_id[faces[f_debug][1]],
    #         vertex_branch_id[faces[f_debug][2]])

    # --- Paso 2: caras semilla de la tráquea (tocando arriba en la tráquea)
   
    # seed_faces = [i for i in range(n_faces) if face_branch_id[i] == id_trachea]
    # distancia de cada vértice al origen
    dist_to_origin = branches[0]["points"][0]
    # umbral automático: 10% de las distancias más pequeñas
    R0 = np.percentile(distances, 10)
    seed_faces = [
        i for i, face in enumerate(faces)
        if np.mean([xis_centerline[v] for v in face]) < 0.05
        and all(branch_ids_list[v] == id_trachea for v in face)
    ]
    #seed_faces = [i for i in range(n_faces) if face_branch_id[i] == id_trachea]
    #seed_faces = [
    #    i for i, face in enumerate(faces)
    #    if np.mean([np.linalg.norm(vertices[v]-dist_to_origin) for v in face]) < R0
    #]
    #print("Seed faces:", seed_faces[:20])
    
    # export_seed_faces(vertices, faces, seed_faces, "seed_faces.vtp")

    print("acabo el export seed faces")

    # --- Paso 3: flood fill
    queue = list(seed_faces)
    visited = set()

    #trachea_cl = np.array(branches[0]["points"])
    #child_cls = [np.array(b["points"]) for b in branches[1:]]
    #epsilon = 0.2 * np.median(distances)
    
    id_father = id_trachea
    id_left   = 52
    id_right  = 60
    
    count_changes = 0
    step   = 0
    step_b = 0
    
    print("Entro al flood fill")
    print("branches[0]['id'] =", branches[0]["id"])
    print("id_trachea:", id_trachea)
    print("ids únicos en face_branch_id (inicial):", set(face_branch_id))
    
    while queue:
        f = queue.pop(0)
        
        # si ya procesaste esta cara, sáltala
        if f in visited:
            continue
        
        # marcar la cara actual como visitada
        visited.add(f)       
     
        parent_bid = face_branch_id[f]   # rama padre
        vertex_update[faces[f][:]] = parent_bid
        # if f == f_debug:
        #     print("\n=== DEBUG CARA", f_debug, "EN FLOOD-FILL ===")
        #     print("parent_bid:", parent_bid)
        #     print("face_branch_id[debug]:", face_branch_id[f_debug])
        #     print("vertex_branch_id vértices debug:",
        #             vertex_branch_id[faces[f_debug][0]],
        #             vertex_branch_id[faces[f_debug][1]],
        #             vertex_branch_id[faces[f_debug][2]])


        for neigh in face_neighbors[f]:
            neigh = int(neigh)
            if neigh in visited:
                continue
            #rama origen del vecino
            #neigh_bid = face_branch_id[neigh]
            face_neigh = faces[neigh]
            face_parent = faces[f]
            neigh_node_id = np.setdiff1d(face_neigh, face_parent)[0]
            #print("rama origen vecino",neigh_bid)
            #print("id_traquea",id_trachea)
            #diff = np.setdiff1d(face_neigh, face_parent)
            #if len(diff) == 0:
            #    continue  # Evita el error y salta a la siguiente cara
            #neigh_node_id = diff[0]
            old_value = vertex_update[neigh_node_id]
            vals = vertex_update[face_neigh]        # los 3 valores de la cara vecina
            num_father = np.sum(vals == id_father)      # cuántos son 89
            num_right  = np.sum(vals == id_right)       # cuántos son 60
            num_left   = np.sum(vals == id_left)        # cuántos son 52
            
            if vertex_update[neigh_node_id]==id_not_assigned:
                if parent_bid == id_trachea:
                    vertex_update[neigh_node_id] = vertex_branch_id[neigh_node_id] 
                    if neigh_node_id ==455:
                        print("TOCO AL 455 - A")
                    #print("no assignado viniendo de traquea",step,neigh_node_id,":   ",vertex_branch_id[neigh_node_id], ' -> ',vertex_update[neigh_node_id])
                else:
                    vertex_update[neigh_node_id] = parent_bid
                    step_b += 1
                    if neigh == 1731:
                        print("SE CUELA LA TRAQUEA")
                    if neigh_node_id ==455:
                            print("TOCO AL 455 - B")
                    #print("no assignado viniendo de bronqui",step,neigh_node_id,":   ",vertex_branch_id[neigh_node_id], ' -> ',vertex_update[neigh_node_id])
            else:
                #throw Exception("excepcio que hem dit que farem assignant pare")
                #if np.unique(vertex_update[face_neigh])==3: #todos son distintos = > al padre
                 #if len(set(vertex_update[node] for node in face_neigh)) == 3:  #todos son distintos = > al padre
                if len(set(vals)) == 3: 
                     #print("tocado - A")
                     if neigh_node_id ==455:
                         print("TOCO AL 455 - C")
                     if neigh == 1731:
                         print("Cara vecina (face_neigh):", face_neigh)
                         print("vertex_branch_id de face_neigh:", vertex_branch_id[face_neigh])
                         print("vertex_update de face_neigh:", vertex_update[face_neigh])
                         print("SE CUELA LA TRAQUEA-A")
                     vertex_update[neigh_node_id] = id_father # OJO parent_bid

                # B: exactamente 1 vértice = id_father (89)
                elif np.sum(vals == id_father) == 1:
                     #print("tocado - B (1 vértice = 89)")
                     if neigh == 1731:
                         print("Cara vecina (face_neigh):", face_neigh)
                         print("vertex_branch_id de face_neigh:", vertex_branch_id[face_neigh])
                         print("vertex_update de face_neigh:", vertex_update[face_neigh])
                         print("SE CUELA LA TRAQUEA-B")
                     vertex_update[neigh_node_id] = id_father
                     if neigh_node_id ==455:
                         print("TOCO AL 455 - D")

                # C: exactamente 1 vértice = id_left (52)
                elif np.sum(vals == id_left) == 1:
                    vertex_update[neigh_node_id] = id_left
                    #print("Cara vecina (face_neigh):", face_neigh)
                    #print("vertex_branch_id de face_neigh:", vertex_branch_id[face_neigh])
                    #print("vertex_update de face_neigh:", vertex_update[face_neigh])
                    #print("tocado - C (1 vértice = 52)")
                    step_b += 1
                    if neigh_node_id ==455:
                        print("TOCO AL 455 - E")

                # D: exactamente 1 vértice = id_right (60)
                elif np.sum(vals == id_right) == 1:
                    vertex_update[neigh_node_id] = id_right
                    #print("Cara vecina (face_neigh):", face_neigh)
                    #print("vertex_branch_id de face_neigh:", vertex_branch_id[face_neigh])
                    #print("vertex_update de face_neigh:", vertex_update[face_neigh])
                    #print("tocado - D (1 vértice = 60)")   
                    step_b += 1
                    if neigh_node_id ==455:
                        print("TOCO AL 455 - F")
   
                # if len(np.setdiff1d(vertex_update[face_neigh], id_father)) == 1:
                #          other = np.setdiff1d(vertex_update[face_neigh], id_father)[0]
                #          vertex_update[neigh_node_id] = id_father 
                #          print("no tocado - B")
                #          print(neigh_node_id,":   ",step,vertex_branch_id[neigh_node_id], ' -> ',vertex_update[neigh_node_id])
                #      elif len(np.setdiff1d(vertex_update[face_neigh], id_left)) == 1:
                #          print("Cara vecina (face_neigh):", face_neigh)
                #          print("vertex_branch_id de face_neigh:", vertex_branch_id[face_neigh])
                #          print("vertex_update de face_neigh:", vertex_update[face_neigh])
                #          #print(vertex_branch_id[faces[f][0]],vertex_branch_id[faces[f][1]],vertex_branch_id[faces[f][2]])
                #          #print(vertex_update[face_neigh])
                #          vertex_update[neigh_node_id] = id_left
                #          print(neigh_node_id,":   ",step,vertex_branch_id[neigh_node_id], ' -> ',vertex_update[neigh_node_id])
                #          print("no tocado - C")
                #      else:
                #          vertex_update[neigh_node_id] = id_right
                #          print(neigh_node_id,":   ",step,vertex_branch_id[neigh_node_id], ' -> ',vertex_update[neigh_node_id])
                #          print("no tocado - D")
                    # if np.length( np.setdiff1d(vertex_update[face_neigh],id_father) ) ==1:
                    #     vertex_update[neigh_node_id] = id_father
                    # elif np.length( np.setdiff1d(vertex_update[face_neigh],id_left) ) ==1:
                    #     vertex_update[neigh_node_id] = id_left
                    # else:
                    #     vertex_update[neigh_node_id] = id_right
            if vertex_update[neigh_node_id] != old_value:
                step   += 1

            #     #print("pasos del flood-fill", step)
            #     #export_debug_step(step, faces, vertices, vertex_update)
            #if step_b > 1 and step_b < 200:
            #    export_debug_step(step, faces, vertices, vertex_update)

            #         print(neigh_node_id,":   ",vertex_branch_id[neigh_node_id], ' -> ',vertex_update[neigh_node_id])
            #         raise Exception("Debug STOP en step 100")
                #export_debug_step(step, faces, vertices, vertex_update)
            #if  vertex_update[neigh_node_id] != vertex_branch_id[neigh_node_id]:
            #    print(neigh_node_id,":   ",vertex_branch_id[neigh_node_id], ' -> ',vertex_update[neigh_node_id])
            
            face_branch_id[neigh] = vertex_update[neigh_node_id]

            #visited.add(neigh)
            # solo añadir vecinas NO visitadas
            if neigh not in visited:
                queue.append(neigh)          
                
    #vertex_update[455]  = 60 #OJOOO
    # vertex_update[463]  = 60 #OJOOO
    # vertex_update[2276] = 60 #OJOOO
    # vertex_update[2266] = 60 #OJOOO
    # vertex_update[2281] = 60 #OJOOO
    # vertex_update[2323] = 60 #OJOOO
    # vertex_update[2391] = 60 #OJOOO
    # vtk_array = vtk.vtkIntArray()
    # vtk_array.SetName("BranchId")
    # vtk_array.SetNumberOfValues(len(vertex_branch_id))

    # for i, bid in enumerate(vertex_branch_id):
    #     vtk_array.SetValue(i, int(bid))
    # polydata.GetPointData().AddArray(vtk_array)
   

    #print("DEBUG: escrito debug_face_branch_id.vtp")
    return vertex_update , face_branch_id

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
    #for f_id in range(len(face_branch_id)):
    #    face = faces[f_id]
    for f_id, face in enumerate(faces):
        # rama correcta para esta cara
        bid = face_branch_id[f_id]
        branch = branches_by_id[bid]
        #cylinder = cylinders_by_id[bid]   # objeto CylinderBranch

        # proyectar los 3 vértices de la cara usando ESTA rama
        for v_id in face:

            if projected[v_id]:
                continue
            
            #bid = face_branch_id[f_id]
            #branch = branches_by_id[bid]
            #cylinder = cylinders_by_id[bid]   # objeto CylinderBranch

            # --- Proyección sobre la centerline de su rama ---
            result = project_on_branches(vertices[v_id], [branch])
            if result is None:
                # Si no se puede proyectar, mantener el vértice original
                new_vertices[v_id] = vertices[v_id]
                projected[v_id] = True
                continue

            _, xi, _, vproj, _, _ = result

            # --- Proyección al cilindro correspondiente ---
            new_vertices[v_id] = map_point_to_cylinder(
                branch,
                xi,
                vproj,
                branches,
                list(cylinders_by_id.values())
            )

            projected[v_id] = True

    return new_vertices

# def recompute_projection_attributes(synthetic_vertices,
#                                     vertex_branch_id,
#                                     branches,
#                                     cylinders_by_id):
#     """
#     Recalcula xi_cilindro, distances y projection_vectors
#     usando la rama limpia (vertex_branch_id).
#     """

#     branches_by_id = {b["id"]: b for b in branches}

#     N = len(synthetic_vertices)
#     xi_cilindro_clean = np.zeros(N)
#     distances_clean = np.zeros(N)
#     projection_vectors_clean = np.zeros((N, 3))

#     for v_id in range(N):

#         bid = vertex_branch_id[v_id]
#         # --- FIX: Si el vértice no tiene rama asignada (-1), saltar o asignar valores por defecto ---
#         if bid == -1 or bid not in branches_by_id:
#             print("cacaaaaa - punto sin brach ID")
#             xi_cilindro_clean[v_id] = np.nan
#             distances_clean[v_id] = np.nan
#             projection_vectors_clean[v_id] = [0.0, 0.0, 0.0]
#             continue
#         # ---------------------------------------------------------------------------------------------
#         branch = branches_by_id[bid]
#         cylinder = cylinders_by_id[bid]
#         x = synthetic_vertices[v_id]
#         # Proyección sobre la centerline de la rama correcta
#         result = project_on_branches(synthetic_vertices[v_id], [branch])
#         if result is None:
#             print("result None recompute attributes")
#             xi_cilindro[v_id] = 0.0
#             distances_clean[v_id] = 0.0
#             projection_vectors_clean[v_id] = np.array([0,0,0])
#             continue
#         branch, xi, p, v, d , outside = result

#         if outside:
#             print("Proyección fuera del segmento:", outside, v_id)
            
#         _, xi, _, vproj_real, _ , _ = result
#         xi_cilindro_clean[v_id] = xi
        
#         # 2) punto del eje del CILINDRO sintético
#         center = cylinder.point(xi)
#         u = cylinder.direction

#         # 3) vector desde el eje del cilindro al vértice sintético
#         v = x - center

#         # descomposición respecto al eje del cilindro
#         v_parallel = np.dot(v, u) * u
#         v_perp = v - v_parallel

#         # distancia radial respecto al cilindro sintético
#         n = np.linalg.norm(v_perp)
#         distances_clean[v_id] = n

#         # vector de proyección "radial" (lo que usas en map_point_to_cylinder)
#         projection_vectors_clean[v_id] = v_perp
        
#         # xi_cilindro_clean[v_id] = xi
#         # distances_clean[v_id] = d
#         # projection_vectors_clean[v_id] = vproj - synthetic_vertices[v_id]

#     return xi_cilindro_clean, distances_clean, projection_vectors_clean
def recompute_on_synthetic(synthetic_vertices,
                           vertex_branch_id,
                           cylinders_by_id):

    N = len(synthetic_vertices)

    xi_cilindro_clean = np.zeros(N)
    distances_clean = np.zeros(N)
    projection_vectors_clean = np.zeros((N, 3))

    for v_id in range(N):

        bid = vertex_branch_id[v_id]

        if bid == -1:
            xi_cilindro_clean[v_id] = np.nan
            distances_clean[v_id] = np.nan
            projection_vectors_clean[v_id] = [0,0,0]
            continue

        cylinder = cylinders_by_id[bid]
        x = synthetic_vertices[v_id]

        # 1) xi sintético
        xi = cylinder.project(x)  
        if v_id == 455:
            print("en recompute el xi",x,xi)
        xi_cilindro_clean[v_id] = xi

        # 2) punto del eje
        center = cylinder.point(xi)
        u = cylinder.direction

        # 3) vector radial
        v = x - center
        v_parallel = np.dot(v, u) * u
        v_perp = v - v_parallel

        # 4) distancia radial
        distances_clean[v_id] = np.linalg.norm(v_perp)

        # 5) vector de proyección radial
        projection_vectors_clean[v_id] = v_perp

    return xi_cilindro_clean, distances_clean, projection_vectors_clean

def map_vertices_to_cylinders(vertices, vertex_branch_id, xis_cilindro, projection_vectors, branches, cylinders_by_id):
    """
    Mapea cada vértice a su cilindro correspondiente según su vertex_branch_id.
    branches_by_id = {b["id"]: b for b in branches}
    """
    branches_by_id = {b["id"]: b for b in branches}
    new_vertices = vertices.copy()
    #cylinders_list = list(cylinders_by_id.values()) if isinstance(cylinders_by_id, dict) else cylinders_by_id
    cylinders_list = list(cylinders_by_id.values())
    
    for i, x in enumerate(vertices):
        bid = vertex_branch_id[i]
        
        if bid == -1:
            continue  # No se modifica el vértice si no tiene rama asignada
            
        # Buscar el objeto branch según el ID del vértice
        #branch = next((b for b in branches if b["id"] == bid), None)
        branch = branches_by_id.get(bid)
        # if i == 455 :
        #     print("en map_vertices_2_cyl",branch,bid)
        
        if branch is None:
            continue
        # # Reproyectar SIEMPRE contra la rama final, no reutilizar valores antiguos
        # result = project_on_branches(x, [branch])

        # if result is None:
        #     continue
        # _, xi, _, v, _ , _ = result
        # if i == 455 :
        #     print("en map_vertices_2_cyl",branch,xi,v)

        xi = xis_cilindro[i]
        v = projection_vectors[i]
        
        # Mapeo puntual por vértice
        new_vertices[i] = map_point_to_cylinder(
            branch,
            xi,
            v,
            branches,
            cylinders_list
        )
        # if i == 455 :
        #     print("las new_coordss",new_vertices[i])
            
       
    return new_vertices


