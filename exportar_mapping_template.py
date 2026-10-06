import vtk
import numpy as np

def export_mapping_template_vtp(mapped_points,
                                projection_vectors=None,
                                xis=None,
                                branch_ids=None,
                                filename="mapping_template.vtp"):
    """
    Exporta los puntos mapeados sobre el cilindro template a un archivo VTP.
    incluyendo coloración por xi_template y branch_id.
    """

    poly = vtk.vtkPolyData()

    # --- Puntos mapeados ---
    vtk_points = vtk.vtkPoints()
    for x in mapped_points:
        vtk_points.InsertNextPoint(float(x[0]), float(x[1]), float(x[2]))
    poly.SetPoints(vtk_points)

    # --- Campo xi_template ---
    xi_arr = vtk.vtkFloatArray()
    xi_arr.SetName("xi_template")
    for xi in xis:
        xi_arr.InsertNextValue(float(xi))
    poly.GetPointData().AddArray(xi_arr)
    
    # --- Campo branch_id ---
    bid_arr = vtk.vtkIntArray()
    bid_arr.SetName("branch_id")
    for bid in branch_ids:
        bid_arr.InsertNextValue(int(bid))
    poly.GetPointData().AddArray(bid_arr)

    # --- Opcional: vectores de proyección ---
    if projection_vectors is not None:
        vec_arr = vtk.vtkFloatArray()
        vec_arr.SetName("projection_vector")
        vec_arr.SetNumberOfComponents(3)

        for v in projection_vectors:
            vec_arr.InsertNextTuple([float(v[0]), float(v[1]), float(v[2])])

        poly.GetPointData().AddArray(vec_arr)


    # --- Guardar ---
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()

    print(f"Archivo guardado: {filename}")

