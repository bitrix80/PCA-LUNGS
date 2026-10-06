import vtk 
def export_original_with_xi(vertices,
                            xis,
                            branch_ids,
                            filename="original_with_xi.vtp"):

    poly = vtk.vtkPolyData()

    # puntos originales
    vtk_points = vtk.vtkPoints()
    for x in vertices:
        vtk_points.InsertNextPoint(float(x[0]), float(x[1]), float(x[2]))
    poly.SetPoints(vtk_points)

    # xi original
    xi_arr = vtk.vtkFloatArray()
    xi_arr.SetName("xi_original")
    for xi in xis:
        xi_arr.InsertNextValue(float(xi))
    poly.GetPointData().AddArray(xi_arr)

    # branch id original
    bid_arr = vtk.vtkIntArray()
    bid_arr.SetName("branch_id")
    for bid in branch_ids:
        bid_arr.InsertNextValue(int(bid))
    poly.GetPointData().AddArray(bid_arr)

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()

    print("Archivo guardado:", filename)

