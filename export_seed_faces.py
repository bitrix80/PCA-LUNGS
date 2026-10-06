import vtk

def export_seed_faces(vertices, faces, seed_faces, filename="seed_faces.vtp"):
    # Crear PolyData
    points = vtk.vtkPoints()
    for v in vertices:
        points.InsertNextPoint(v[0], v[1], v[2])

    polys = vtk.vtkCellArray()
    for f in faces:
        polys.InsertNextCell(3)
        polys.InsertCellPoint(int(f[0]))
        polys.InsertCellPoint(int(f[1]))
        polys.InsertCellPoint(int(f[2]))

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    polydata.SetPolys(polys)

    # Crear array escalar para marcar las seed faces
    scalars = vtk.vtkIntArray()
    scalars.SetName("seed_face")
    scalars.SetNumberOfValues(len(faces))

    for i in range(len(faces)):
        if i in seed_faces:
            scalars.SetValue(i, 1)
        else:
            scalars.SetValue(i, 0)

    polydata.GetCellData().SetScalars(scalars)

    # Guardar VTP
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(polydata)
    writer.Write()

    print("Exportado:", filename)
