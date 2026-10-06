import numpy as np
import vtk

from vtk_io import read_stl

from centerline import (
    read_all_branches,
    root_branch,
)

from geometry import project_on_branches


CENTERLINE = "Huca0506660.vtp"
STL = "Huca0506660_preprocessed.stl"


# ==========================================================
# Escriure segments x --> p
# ==========================================================

def write_segments(filename, segments):

    points = vtk.vtkPoints()
    lines = vtk.vtkCellArray()

    pid = 0

    for a, b in segments:

        points.InsertNextPoint(a)
        points.InsertNextPoint(b)

        line = vtk.vtkLine()
        line.GetPointIds().SetId(0, pid)
        line.GetPointIds().SetId(1, pid + 1)

        lines.InsertNextCell(line)

        pid += 2

    poly = vtk.vtkPolyData()
    poly.SetPoints(points)
    poly.SetLines(lines)

    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()


# ==========================================================
# Validar projecció sobre UNA branca
# ==========================================================

def validate_projection(branches, vertices):

    segments = []

    for x in vertices[::300]:

        result = project_on_branches(
            x,
            branches
        )

        if result is None:
            continue

        branch, xi, p, v, d = result

        segments.append((x, p))

        print("----------------------")
        print("xi =", xi)
        print("distància =", d)
        print("punt STL =", x)
        print("punt projectat =", p)

    write_segments(
        "projection_segments.vtp",
        segments
    )

    print()
    print(len(segments), "segments escrits.")


# ==========================================================
# MAIN
# ==========================================================

def main():

    branches = read_all_branches(CENTERLINE)

    

    _, vertices, _ = read_stl(STL)

    validate_projection(
        branches,
        vertices
    )


if __name__ == "__main__":
    main()