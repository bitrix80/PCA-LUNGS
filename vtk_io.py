"""

Lectura i escriptura de fitxers STL i VTP.

"""

import vtk
import numpy as np
from vtk.util.numpy_support import vtk_to_numpy, numpy_to_vtk


# ==========================================================
# STL
# ==========================================================

def read_stl(filename):
    """
    Llegeix una STL.

    Returns
    -------
    polydata : vtkPolyData

    points : ndarray (N,3)

    faces : list[list[int]]
        Connectivitat dels triangles.
    """

    reader = vtk.vtkSTLReader()
    reader.SetFileName(filename)
    reader.Update()

    poly = reader.GetOutput()

    points = vtk_to_numpy(poly.GetPoints().GetData())

    faces = []

    polys = poly.GetPolys()
    polys.InitTraversal()

    idlist = vtk.vtkIdList()

    while polys.GetNextCell(idlist):

        face = []

        for i in range(idlist.GetNumberOfIds()):
            face.append(idlist.GetId(i))

        faces.append(face)

    return poly, points.copy(), faces


# ==========================================================
# Escriure STL
# ==========================================================

def write_stl(filename,
              template_polydata,
              new_points):
    """
    Escriu una STL mantenint la connectivitat original.

    Parameters
    ----------

    template_polydata

    new_points : ndarray (N,3)
    """

    pts = vtk.vtkPoints()

    pts.SetData(
        numpy_to_vtk(
            new_points,
            deep=True
        )
    )

    poly = vtk.vtkPolyData()

    poly.DeepCopy(template_polydata)

    poly.SetPoints(pts)

    writer = vtk.vtkSTLWriter()

    writer.SetFileName(filename)

    writer.SetInputData(poly)

    writer.Write()


# ==========================================================
# VTP
# ==========================================================

def read_centerline(filename):
    """
    Llegeix un centerline VTP.

    Returns
    -------

    poly : vtkPolyData

    points : ndarray (N,3)

    lines : list[list[int]]

    branch_ids : ndarray

    parent_branch_ids : ndarray

    generation_ids : ndarray
    """

    reader = vtk.vtkXMLPolyDataReader()

    reader.SetFileName(filename)

    reader.Update()

    poly = reader.GetOutput()

    points = vtk_to_numpy(
        poly.GetPoints().GetData()
    ).copy()

    # ------------------------------------------------------
    # Llegim totes les línies
    # ------------------------------------------------------

    lines = []

    cells = poly.GetLines()

    cells.InitTraversal()

    ids = vtk.vtkIdList()

    while cells.GetNextCell(ids):

        line = []

        for i in range(ids.GetNumberOfIds()):

            line.append(
                ids.GetId(i)
            )

        lines.append(line)
    # ------------------------------------------------------
    # Arrays CellData
    # ------------------------------------------------------

    cell_data = poly.GetCellData()

    branch_ids = vtk_to_numpy(
        cell_data.GetArray("BranchId")
    )

    parent_branch_ids = vtk_to_numpy(
        cell_data.GetArray("ParentBranchId")
    )

    generation_ids = vtk_to_numpy(
        cell_data.GetArray("GenerationId")
    )

    return (
        poly,
        points,
        lines,
        branch_ids,
        parent_branch_ids,
        generation_ids
    )


# ============================================================
# Escriure VTP amb camps --per tenir el camp de distància per cada punt
# ============================================================

def write_vtp(filename,
              polydata,
              vertices,
              distances,
              xis,
              branch_ids,
              projection_vectors,
              extra_point_data=None):

    import vtk
    from vtk.util.numpy_support import numpy_to_vtk
    import numpy as np

    # --------------------------------------------------------
    # Crear nuevo polydata
    # --------------------------------------------------------
    poly = vtk.vtkPolyData()

    # --------------------------------------------------------
    # Puntos
    # --------------------------------------------------------
    vtk_points = vtk.vtkPoints()
    vtk_points.SetData(numpy_to_vtk(vertices.astype(np.float32), deep=True))
    poly.SetPoints(vtk_points)

    # --------------------------------------------------------
    # Caras (copiamos las del polydata original)
    # --------------------------------------------------------
    poly.SetPolys(polydata.GetPolys())

    # --------------------------------------------------------
    # Campo: distancia
    # --------------------------------------------------------
    vtk_dist = numpy_to_vtk(distances.astype(np.float32))
    vtk_dist.SetName("Distance")
    poly.GetPointData().AddArray(vtk_dist)

    # --------------------------------------------------------
    # Campo: xi
    # --------------------------------------------------------
    vtk_xi = numpy_to_vtk(xis.astype(np.float32))
    vtk_xi.SetName("Xi")
    poly.GetPointData().AddArray(vtk_xi)

    # --------------------------------------------------------
    # Campo: branch_id
    # --------------------------------------------------------
    vtk_bid = numpy_to_vtk(branch_ids.astype(np.int32))
    vtk_bid.SetName("BranchId")
    poly.GetPointData().AddArray(vtk_bid)

    # --------------------------------------------------------
    # Campo: projection vector
    # --------------------------------------------------------
    vtk_vec = numpy_to_vtk(projection_vectors.astype(np.float32))
    vtk_vec.SetNumberOfComponents(3)
    vtk_vec.SetName("ProjectionVector")
    poly.GetPointData().AddArray(vtk_vec)

    # --------------------------------------------------------
    # NUEVO: campos extra
    # --------------------------------------------------------
    if extra_point_data is not None:
        for name, array in extra_point_data.items():
            vtk_array = numpy_to_vtk(array.astype(np.float32))
            vtk_array.SetName(name)
            poly.GetPointData().AddArray(vtk_array)

    # --------------------------------------------------------
    # Escribir fichero
    # --------------------------------------------------------
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()


    

# ==========================================================
# Guardar qualsevol PolyData
# ==========================================================

def write_polydata(filename,
                   poly):

    writer = vtk.vtkXMLPolyDataWriter()

    writer.SetFileName(filename)

    writer.SetInputData(poly)

    writer.Write()

#Camp vectors projecció sobre malla original

def write_projection_vectors(filename,
                             template_polydata,
                             projection_vectors):
    """
    Escriu la mateixa geometria original afegint
    un camp vectorial ProjectionVector.
    """

    poly = vtk.vtkPolyData()
    poly.DeepCopy(template_polydata)

    vtk_vectors = numpy_to_vtk(
        projection_vectors,
        deep=True
    )

    vtk_vectors.SetNumberOfComponents(3)
    vtk_vectors.SetName("ProjectionVector")

    poly.GetPointData().AddArray(vtk_vectors)

    writer = vtk.vtkXMLPolyDataWriter()

    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()

# ==========================================================
# Utilitats
# ==========================================================

def numpy_to_points(array):
    """
    ndarray -> vtkPoints
    """

    pts = vtk.vtkPoints()

    pts.SetData(
        numpy_to_vtk(
            array,
            deep=True
        )
    )

    return pts


def points_to_numpy(vtk_points):
    """
    vtkPoints -> ndarray
    """

    return vtk_to_numpy(
        vtk_points.GetData()
    ).copy()


# ==========================================================
# Debug
# ==========================================================

def print_centerline_info(filename):

    (
        poly,
        points,
        lines,
        branch,
        parent,
        generation
    ) = read_centerline(filename)

    print()

    print("====================================")

    print("CENTERLINE")

    print("====================================")

    print()

    print("Nombre de punts")

    print(len(points))

    print()

    print("Nombre de línies")

    print(len(lines))

    print()

    print("Branques úniques")

    print(np.unique(branch))

    print()

    print("Parents")

    print(np.unique(parent))

    print()

    print("Generacions")

    print(np.unique(generation))

    print()

    for i in range(min(10, len(lines))):

        print("--------------------------------")

        print("Línia", i)

        print("BranchId :", branch[i])

        print("Parent   :", parent[i])

        print("Generation :", generation[i])

        print("Nombre punts :", len(lines[i]))
