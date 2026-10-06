from vtk_io import read_stl
from vtk_io import write_vtp

from centerline import (
    read_all_branches,
    root_branch,
    children
)

from cylinder import first_three_cylinders

from mapping import map_mesh_vertices
from mapping import compute_projection_vectors
from detect_bifurcation_vertices import detect_bifurcation_vertices
from vtk_io import write_projection_vectors

import numpy as np

CENTERLINE = "Huca0506660.vtp"
STL = "Huca0506660_preprocessed.stl"
OUTPUT = "mapped_geometry.stl"


def main():

    print("Llegint centerline...")

    branches = read_all_branches(CENTERLINE)

    print("Nombre total de branques:", len(branches))

    # Seleccionem només les 3 que volem
    root = root_branch(branches)

    childs = children(branches, root["id"])

    branches = [
        root,
        childs[0],
        childs[1]
    ]

    print("Branques utilitzades:",
        [b["id"] for b in branches])

    print("Construint cilindres...")

    cylinders = first_three_cylinders(branches)


    print("Llegint STL...")

    polydata, vertices, faces = read_stl(STL)

    projection_vectors = compute_projection_vectors(
        vertices,
        branches
    )

    write_projection_vectors(
        "original_projection_vectors.vtp",
        polydata,
        projection_vectors
    )

    print("Nombre de vèrtexs:", len(vertices))
    print("Detectando vértices en bifurcación...")
    bif_vertices = detect_bifurcation_vertices(
       vertices,
       branches,
       cylinders,
       branch_ids,
       xis,
       faces
    )
    is_bifurcation = np.zeros(len(vertices), dtype=np.float32)
    is_bifurcation[bif_vertices] = 1.0
    print("Vértices detectados:", bif_vertices)
    
    write_vtp(
      "bifurcation_vertices.vtp",
      polydata,
      new_vertices,
      is_bifurcation,
      xis,
      branch_ids,
      projection_vectors
    )
    print("Projectant punts...")

    new_vertices, distances, xis, branch_ids, projection_vectors = map_mesh_vertices(
        vertices,
        branches,
        cylinders
    )

    # Distancia entre coordenada original y coordenada mapeada
    dist_original_vs_mapped = np.linalg.norm(vertices - new_vertices, axis=1)

    print("Distancia original vs mapeada:")
    print("  Mínima :", np.nanmin(dist_original_vs_mapped))
    print("  Máxima :", np.nanmax(dist_original_vs_mapped))
    print("  Media  :", np.nanmean(dist_original_vs_mapped))
    print("  P90    :", np.nanpercentile(dist_original_vs_mapped, 90))
    print("  P99    :", np.nanpercentile(dist_original_vs_mapped, 99))

    idx_max = np.argmax(dist_original_vs_mapped)
    print("Indice del vértice con distancia máxima:", idx_max)
    print("Distancia máxima:", dist_original_vs_mapped[idx_max])
    print("Branch ID:", branch_ids[idx_max])
    print("xi:", xis[idx_max])
    print("distancia al centerline:", distances[idx_max])
    caras_con_ese_vertice = np.where(faces == idx_max)[0]
    # --- Campo escalar para marcar el vértice problemático ---
    is_problematic_vertex = np.zeros(len(vertices), dtype=np.float32)
    is_problematic_vertex[idx_max] = 1.0 
    # --- Campo escalar para marcar las caras problemáticas ---
    is_problematic_face = np.zeros(len(faces), dtype=np.float32)
    print("Caras que contienen ese vértice:", caras_con_ese_vertice)
    print("\n--- Comprobación completa de todas las caras ---")
    for cara in caras_con_ese_vertice:
     v0, v1, v2 = faces[cara]
     is_problematic_face[cara] = 1.0
     #print(f"Cara {cara}:",
     #     v0 == idx_max,
     #     v1 == idx_max,
     #     v2 == idx_max)  
     #print("¿Contiene realmente el vértice 4193?")
     #print(v0 == idx_max, v1 == idx_max, v2 == idx_max)
     #print("Indices de la cara:", faces[cara])
     #print("¿Contiene realmente el vértice 4193?:",
     #     faces[cara][0] == idx_max,
     #     faces[cara][1] == idx_max,
     #     faces[cara][2] == idx_max)
     print(f"\nCara {cara}:")
     print("  ORIGINAL:")
     print("    v0:", vertices[v0])
     print("    v1:", vertices[v1])
     print("    v2:", vertices[v2])
     print("  MAPEADA:")
     print("    v0:", new_vertices[v0])
     print("    v1:", new_vertices[v1])
     print("    v2:", new_vertices[v2])


    print("Escrivint VTP...")

    print(type(new_vertices))
    print(new_vertices.dtype)
    print(new_vertices.shape)
    print(new_vertices[:5])

    write_vtp(
        "mapped_geometry.vtp",
        polydata,
        new_vertices,
        distances,
        xis,
        branch_ids,
        projection_vectors
    )


    print("Acabat.")


if __name__ == "__main__":
    main()
