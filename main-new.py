from vtk_io import read_stl
from vtk_io import write_vtp

from centerline import (
    read_all_branches,
    root_branch,
    children
)

import numpy as np
import vtk
import pyvista as pv 

from cylinder import first_three_cylinders

from mapping import map_mesh_vertices
from mapping import compute_projection_vectors
from detect_bifurcation_vertices import detect_bifurcation_vertices
from vtk_io import write_projection_vectors
from cylinders_export import cylinder_to_polydata
from oriented_centerline import build_ordered_indices
from centerline import read_centerline
from mapping import (
    map_point_to_cylinder,
    map_points_verbose,
    assign_branch_by_faces,
    build_face_neighbors,
    export_face_branch_id,
    map_mesh_vertices,
    compute_projection_vectors,
    assign_branch_by_faces,
    map_faces_to_cylinders,
    map_vertices_to_cylinders,
    recompute_on_synthetic,
)
from exportar_caras_mezcladas import exportar_caras_mezcladas_vtp
from exportar_mapping_template import export_mapping_template_vtp
from exportar_original_with_xi import export_original_with_xi
from export import export_stl

CENTERLINE = "Huca0506660.vtp"
STL = "Huca0506660_preprocessed.stl"
OUTPUT = "mapped_geometry.stl"


def main():

    print("Llegint centerline...")

    poly_vtk = read_centerline(CENTERLINE)
    poly = pv.wrap(poly_vtk)

    ordered_indices, root_bid, parent_map = build_ordered_indices(poly)

    branches = read_all_branches(CENTERLINE, ordered_indices)

    
    root = root_branch(branches)
    childs = children(branches, root["id"])

    branches = [root, childs[0], childs[1]]

    print("\n=== BIFURCACIÓN REAL ===")
    bif = branches[0]["points"][-1]
    print("bif =", bif)
    print("Branques utilitzades:", [b["id"] for b in branches])
    for b in branches:
        pts = b["points"]
        print(f"Branch {b['id']}:")
        print("  start =", pts[0])
        print("  end   =", pts[-1])
    
    print("Construint cilindres...")
    cylinders = first_three_cylinders(branches)
    cylinders_by_id = {cyl.id: cyl for cyl in cylinders}
    for cyl in cylinders:
        print("Cylinder ID:", cyl.id)
        print("ID:", cyl.id, "direction:", cyl.direction)
        origin = cyl.origin
        direction = cyl.direction
        length = cyl.length
        branch_id = cyl.id
        print("datos-cilindro:",origin,direction,length,branch_id)
        poly = cylinder_to_polydata(origin, direction, length, branch_id)

        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(f"cylinder_{branch_id}.vtp")
        writer.SetInputData(poly)
        writer.Write()

    print("Cilindres exportats.")

    print("Llegint STL...")
    polydata, vertices, faces = read_stl(STL)
    print("Num caras:", len(faces))
   # projection_vectors = compute_projection_vectors(vertices, branches)
   # write_projection_vectors("original_projection_vectors.vtp", polydata, projection_vectors)
    
    # 2. Construir vecinos de caras
    face_neighbors = build_face_neighbors(faces)

    # 3. Proyección sobre ramas
    projection_vectors, mapped_points,xis_list, branch_ids_list = compute_projection_vectors(
        vertices,
        branches,
        cylinders_by_id
    )
    print("Antes:", np.unique(branch_ids_list))
    # 4. Limpieza por elementos (flood-fill)
    new_points, xis_list, branch_ids_list, distances, projection_vectors = map_points_verbose(
        vertices,
        branches,
        cylinders_by_id
    )

 
    export_original_with_xi(
        vertices,
        xis_list,
        branch_ids_list,
        filename="original_clean_branch.vtp"
    )

    # 5. DEBUGG: exportar branch_id por cara
    face_branch_id = []
    for face in faces:
        bids = [branch_ids_list[v] for v in face]
        # mayoría por cara
        bid = max(set(bids), key=bids.count)
        face_branch_id.append(bid)

    export_face_branch_id(faces, face_branch_id, vertices,
                      "debug_face_branch_id.vtp")

    # 6. Exportar STL original con branch_id limpio
    export_original_with_xi(
        vertices,
        xis_list,
        branch_ids_list,
        filename="original_with_xi.vtp"
    )   
    # 7. Exportar mapping template
    export_mapping_template_vtp(
        mapped_points,
        projection_vectors=projection_vectors,
        xis=xis_list,
        branch_ids=branch_ids_list,
        filename="mapping_template.vtp"
    )

    print("Projectant punts...")
    new_vertices, distances, xis_centerline, xi_cilindro, branch_ids, projection_vectors = map_mesh_vertices(
        vertices,
        branches,
        cylinders,
        faces
    )
    print("XI NEW VERTICES",xi_cilindro[455])
    print("hasta aquí sin modificaciones")
    export_stl("geometry_new_vertices.stl", new_vertices, faces)
    print("NEW-VERTICE",branch_ids[455],new_vertices[455])

    # ============================================================
    # FLOOD-FILL POR CARAS: face_branch_id
    # ============================================================

    
    # vertex_branch_id, face_branch_id = assign_branch_by_faces(
    #     faces,
    #     new_vertices,
    #     branch_ids,          # rama por vértice después del peinado
    #     face_neighbors, 
    #     branches[0]["id"],   # id tráquea
    #     branches,
    #     distances,
    #     xis_centerline
    # )
    
    # distances_branch_only = np.zeros(len(vertices))

    # for v_id, x in enumerate(vertices):
    #     bid = vertex_branch_id[v_id]
    #     branch = branches_by_id[bid]

    #     xi, p, v, d, outside = project_on_branch(
    #         x,
    #         branch["points"],
    #         branch["arc"]
    #         )

    #     distances_branch_only[v_id] = d

    #print("Flood-fill completado. Ramas únicas:", np.unique(vertex_branch_id))

    # ============================================================
    # DEBUG: ver asignación de ramas por vértice en la geometría original
    # ============================================================

    # write_vtp(
    #     "debug_original_vertices_branch.vtp",
    #     polydata,               # geometría original
    #     vertices,               # vértices originales
    #     distances,              # 
    #     xis_centerline,         # también los originales
    #     vertex_branch_id,       # rama final por vértice (limpia)
    #     projection_vectors      # originales
    # )

    # print("DEBUG: escrito debug_original_vertices_branch.vtp")
    # export_face_branch_id(
    #     faces,
    #     face_branch_id,
    #     vertices,
    #     "debug_final_face_branch.vtp"
    # )

    # print("DEBUG: escrito debug_original_face_branch.vtp")
    
    # # 3. RECALCULAR xi Y v PARA LA RAMA FINAL
    # xi_cilindro_clean, distances_clean, projection_vectors_clean = \
    #     recompute_on_synthetic(
    #         vertices,          #NO synthetic_vertices
    #         vertex_branch_id,
    #         cylinders_by_id
    #         )
    # print("XI CLEAN",xi_cilindro_clean[455])
    # =======================================================================
    # GEOMETRIA SINTETICA FINAL SIN CARAS MEZCLADAS (usando vertex_branch_id)
    # =======================================================================

# 2. Mapeas usando SOLO la información de los vértices (ya no usas caras)
    # synthetic_vertices = map_vertices_to_cylinders(
    #    vertices,       
    #    vertex_branch_id,
    #    xi_cilindro_clean,
    #    projection_vectors_clean,
    #    branches,
    #    cylinders_by_id
    # )
    # export_stl("geometry_synthetic_vertices.stl", synthetic_vertices, faces)

    # print("SYNTHETIC-VERTICE",vertex_branch_id[455],synthetic_vertices[455])

    # write_vtp(
    #     "debug_synthetic_vertices-0.vtp",
    #     polydata,
    #     synthetic_vertices, #ojo --- synthetic_vertices?
    #     distances,
    #     xi_cilindro,
    #     vertex_branch_id,
    #     projection_vectors
    # )



    print("Geometría sintética recalculada.")


    # print("Atributos limpios recalculados.")
    # # synthetic_vertices: tu geometría sintética
    # # xi_cilindro_clean: array con los xi limpios

    # mask_bad = (xi_cilindro_clean == 0).astype(np.float64)

    # # Crear PolyData con puntos sintéticos
    # cloud = pv.PolyData(synthetic_vertices)

    # # Añadir campo escalar
    # cloud["xi_clean_zero"] = mask_bad

    # # Guardar fichero para ParaView
    # cloud.save("synthetic_vertices_xi_clean_zero.vtp")
    
    # ============================================================
    # DEBUG: exportar synthetic_vertices + vertex_branch_id
    # ============================================================
    # print("DEBUG: escrito debug_synthetic_vertices.vtp")

    # write_vtp(
    #     "debug_synthetic_vertices.vtp",
    #     polydata,
    #     synthetic_vertices,   
    #     distances_clean,
    #     xi_cilindro_clean,
    #     vertex_branch_id,
    #     projection_vectors_clean
    #)

    # ============================================================
    # DEBUG: exportar face_branch_id por cara
    # ============================================================

    # export_face_branch_id(
    #     faces,
    #     face_branch_id,
    #     vertices,
    #     "debug_face_branch_id.vtp"
    # )

    # print("DEBUG: escrito debug_face_branch_id.vtp")

    # def write_point_cloud_vtk(filename, points, vertex_branch_id):
    #     with open(filename, "w") as f:
    #         f.write("# vtk DataFile Version 3.0\n")
    #         f.write("Point cloud\n")
    #         f.write("ASCII\n")
    #         f.write("DATASET POLYDATA\n")
    #         f.write(f"POINTS {len(points)} float\n")
    #         for p in points:
    #             f.write(f"{p[0]} {p[1]} {p[2]}\n")

    #         f.write(f"POINT_DATA {len(points)}\n")
    #         f.write("SCALARS BranchId int\n")
    #         f.write("LOOKUP_TABLE default\n")
    #         for bid in vertex_branch_id:
    #             f.write(f"{int(bid)}\n")


    # caras_mezcladas = []


    # for idx, cara in enumerate(faces):
    #     v0, v1, v2 = cara
    #     ramas = {vertex_branch_id[v0], vertex_branch_id[v1], vertex_branch_id[v2]}
    #     if len(ramas) > 1:
    #         caras_mezcladas.append((idx, ramas))
    #         print("la cara mezcalda",cara)
    #         print("  xi_centerline:", xis_centerline[v0],
    #                                   xis_centerline[v1],
    #                                  xis_centerline[v2])
    #         print("  xi_cilindro:  ", xi_cilindro[v0],
    #                                  xi_cilindro[v1],
    #                                  xi_cilindro[v2])
    #         print("  xi_cilindro_clean:  ", xi_cilindro_clean[v0],
    #                                  xi_cilindro_clean[v1],
    #                                  xi_cilindro_clean[v2])
    #         print("point-distance:"    ,v0, distances[v0],
    #                                v1, distances[v1],
    #                                v2, distances[v2])
    #         print("point-distance_clean:"    ,v0, distances_clean[v0],
    #                                v1, distances_clean[v1],
    #                                v2, distances_clean[v2])

    # print("Caras que mezclan ramas:", len(caras_mezcladas))
    print("Acabat.")
    print("Escrivint VTP...")
    # exportar_caras_mezcladas_vtp(
    #     synthetic_vertices,
    #     faces,
    #     xis_centerline,
    #     xi_cilindro_clean,
    #     caras_mezcladas,
    #     filename="caras_mezcladas.vtp"
    # )
    
    

    # ============================================================
    # 4. EXPORTAR VTP FINAL SIN MEZCLA
    # ============================================================
    write_vtp(
        "mapped_geometry-origin.vtp",
        polydata,
        new_vertices,        # geometría proyectada por vértices
        distances,
        xi_cilindro,
        branch_ids_list,    # rama final por vértice
        projection_vectors
    )

    # write_vtp(
    #     "mapped_geometry.vtp",
    #     polydata,
    #     synthetic_vertices,        # geometría proyectada por vértices
    #     distances_clean,
    #     xi_cilindro_clean,
    #     vertex_branch_id,    # rama final por vértice
    #     projection_vectors_clean
    # )
if __name__ == "__main__":
    main()
