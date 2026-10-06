#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 09:23:51 2026

@author: beatriz
"""

import vtk
import numpy as np

def export_debug_step(step, faces, points, vertex_update):
    # Crear polydata
    poly = vtk.vtkPolyData()

    # Puntos
    vtk_points = vtk.vtkPoints()
    for p in points:
        vtk_points.InsertNextPoint(p)
    poly.SetPoints(vtk_points)

    # Caras
    cells = vtk.vtkCellArray()
    for f in faces:
        tri = vtk.vtkTriangle()
        tri.GetPointIds().SetId(0, int(f[0]))
        tri.GetPointIds().SetId(1, int(f[1]))
        tri.GetPointIds().SetId(2, int(f[2]))
        cells.InsertNextCell(tri)
    poly.SetPolys(cells)

    # Array de vértices
    arr = vtk.vtkIntArray()
    arr.SetName("vertex_update")
    for v in vertex_update:
        arr.InsertNextValue(int(v))
    poly.GetPointData().AddArray(arr)

    # Guardar archivo
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(f"debug_step_{step}.vtp")
    writer.SetInputData(poly)
    writer.Write()