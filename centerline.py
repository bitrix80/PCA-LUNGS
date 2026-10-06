"""

Lectura del centerline VTP i extracció de la branca arrel
i les seves dues filles.

Utilitza geometry.py per calcular la longitud d'arc.

"""

import vtk
import numpy as np
import pyvista as pv

from vtk.util.numpy_support import vtk_to_numpy

from geometry import cumulative_lengths
from oriented_centerline import build_ordered_indices

# ============================================================
# Llegir VTP
# ============================================================

def read_centerline(filename):
    """
    Retorna el vtkPolyData.
    """

    reader = vtk.vtkXMLPolyDataReader()

    reader.SetFileName(filename)

    reader.Update()

    return reader.GetOutput()


# ============================================================
# Llegir una polyline
# ============================================================

def polyline_to_points(polydata,
                       cell_id):
    """
    Retorna els punts corresponents
    a una vtkPolyLine.
    """

    ids = vtk.vtkIdList()

    polydata.GetCellPoints(cell_id,
                           ids)

    pts = np.zeros((ids.GetNumberOfIds(),3))

    for i in range(ids.GetNumberOfIds()):

        pts[i] = polydata.GetPoint(
            ids.GetId(i)
        )

    return pts


# ============================================================
# Llegir totes les branques
# ============================================================

def read_all_branches(filename, ordered_indices):
    """
    Retorna una llista de branques.

    Cada branca és un diccionari:

    {
        "id"
        "parent"
        "generation"
        "points"
        "arc"
        "length"
    }
    """
    #poly = read_centerline(filename)
    poly_vtk = read_centerline(filename)
    poly = pv.wrap(poly_vtk)   #  conversión a PyVista
    #Orientadas
    ordered_indices, root_bid, parent_map = build_ordered_indices(poly)
    
    cell_data = poly.GetCellData()
    branch_ids = vtk_to_numpy(
        cell_data.GetArray("BranchId")
    )
    parent_ids = vtk_to_numpy(
        cell_data.GetArray("ParentBranchId")
    )
    generation_ids = vtk_to_numpy(
        cell_data.GetArray("GenerationId")
    )
    branches = []
    for cell in range(poly.GetNumberOfCells()):
        branch_id = int(branch_ids[cell])
        idx = ordered_indices[branch_id]        # índices reorientados
        pts = poly.points[idx]                  # puntos reorientados
        #pts = np.array([poly.points.GetPoint(i) for i in idx])

        #pts = polyline_to_points(poly, cell)
        arc = cumulative_lengths(pts)
        branch = {
            "id":
            int(branch_ids[cell]),
            "parent":
            int(parent_ids[cell]),
            "generation":
            int(generation_ids[cell]),
            "points":
            pts,
            "arc":
            arc,
            "length":
            arc[-1]
        }
        branches.append(branch)

    return branches

# ============================================================
# Trobar branca arrel
# ============================================================

def root_branch(branches):
    """
    Busca la branca arrel.

    Normalment és la que té
    ParentBranchId = -1.
    """

    for b in branches:

        if b["parent"] < 0:

            return b

    raise RuntimeError(
        "No s'ha trobat la branca arrel."
    )


# ============================================================
# Trobar filles
# ============================================================

def children(branches,
             parent_id):
    """
    Retorna totes les filles
    d'una branca.
    """

    out = []

    for b in branches:

        if b["parent"] == parent_id:

            out.append(b)

    return out


# ============================================================
# Arrel + dues filles
# ============================================================

def first_three_branches(filename):
    """
    Retorna

    root

    child1

    child2

    en aquest ordre.
    """

    branches = read_all_branches(
        filename
    )

    root = root_branch(branches)

    childs = children(
        branches,
        root["id"]
    )

    if len(childs) != 2:

        raise RuntimeError(

            f"La branca arrel té "
            f"{len(childs)} filles "
            f"(esperàvem 2)."

        )

    return [

        root,

        childs[0],

        childs[1]

    ]


# ============================================================
# Debug
# ============================================================

def print_tree(filename):

    branches = read_all_branches(
        filename
    )

    print()

    print("--------------------------------")

    print("BRANQUES")

    print("--------------------------------")

    print()

    for b in branches:

        print(

            "Branch",

            b["id"],

            " Parent",

            b["parent"],

            " Generation",

            b["generation"],

            " Length",

            round(b["length"],2),

            " Npts",

            len(b["points"])

        )

    print()

    root = root_branch(branches)

    print("Root =", root["id"])

    print()

    childs = children(
        branches,
        root["id"]
    )

    print(

        "Filles:",

        [c["id"] for c in childs]

    )


# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    filename = "Huca0506660.vtp"

    print_tree(filename)
