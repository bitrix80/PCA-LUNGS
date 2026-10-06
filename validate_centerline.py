import numpy as np
import vtk

from centerline import (
    read_all_branches,
    root_branch,
    children
)

from geometry import point_from_xi


CENTERLINE = "Huca0506660.vtp"


# ==========================================================
# Escriu una polilínia VTP
# ==========================================================

def write_polyline(filename, points):

    vtk_points = vtk.vtkPoints()

    for p in points:
        vtk_points.InsertNextPoint(
            float(p[0]),
            float(p[1]),
            float(p[2])
        )

    polyline = vtk.vtkPolyLine()
    polyline.GetPointIds().SetNumberOfIds(len(points))

    for i in range(len(points)):
        polyline.GetPointIds().SetId(i, i)

    cells = vtk.vtkCellArray()
    cells.InsertNextCell(polyline)

    poly = vtk.vtkPolyData()
    poly.SetPoints(vtk_points)
    poly.SetLines(cells)

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()


# ==========================================================
# Validació d'una branca
# ==========================================================

def validate_branch(branch, filename):

    print()
    print("====================================")
    print("Branch", branch["id"])
    print("====================================")

    xis = np.linspace(0.0, 1.0, 200)

    curve = []

    for xi in xis:

        curve.append(
            point_from_xi(
                branch["points"],
                branch["arc"],
                xi
            )
        )

    curve = np.asarray(curve)

    write_polyline(
        filename,
        curve
    )

    print()

    print("Extrem inicial")

    print(branch["points"][0])
    print(curve[0])

    print()

    print("Extrem final")

    print(branch["points"][-1])
    print(curve[-1])

    print()

    print("Errors sobre els punts originals")

    errors = []

    total = branch["arc"][-1]

    for i in range(len(branch["points"])):

        xi = branch["arc"][i] / total

        p = point_from_xi(
            branch["points"],
            branch["arc"],
            xi
        )

        err = np.linalg.norm(
            p - branch["points"][i]
        )

        errors.append(err)

    errors = np.asarray(errors)

    print("Error màxim :", errors.max())
    print("Error mitjà :", errors.mean())


# ==========================================================
# MAIN
# ==========================================================

def main():

    branches = read_all_branches(CENTERLINE)

    root = root_branch(branches)

    childs = children(
        branches,
        root["id"]
    )

    branches = [
        root,
        childs[0],
        childs[1]
    ]

    validate_branch(
        branches[0],
        "root_curve.vtp"
    )

    validate_branch(
        branches[1],
        "child1_curve.vtp"
    )

    validate_branch(
        branches[2],
        "child2_curve.vtp"
    )


if __name__ == "__main__":
    main()