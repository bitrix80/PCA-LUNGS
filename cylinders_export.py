import numpy as np
import vtk
from vtk.util.numpy_support import numpy_to_vtk

def cylinder_to_polydata(origin, direction, length, branch_id):
    # Puntos del eje
    p0 = origin
    p1 = origin + direction * length

    points = vtk.vtkPoints()
    points.InsertNextPoint(*p0)
    points.InsertNextPoint(*p1)

    line = vtk.vtkLine()
    line.GetPointIds().SetId(0, 0)
    line.GetPointIds().SetId(1, 1)

    cells = vtk.vtkCellArray()
    cells.InsertNextCell(line)

    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetLines(cells)

    # Añadimos el BranchId como atributo
    bid = numpy_to_vtk(np.array([branch_id, branch_id], dtype=np.int32))
    bid.SetName("BranchId")
    poly.GetPointData().AddArray(bid)

    return poly
