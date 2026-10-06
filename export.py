#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 13:00:55 2026

@author: beatriz
"""

import pyvista as pv

def export_stl(filename, vertices, faces):
    """
    Exporta un STL usando solo coordenadas y conectividad.
    Sin atributos, sin campos, sin colores.
    """
    # PyVista espera un array tipo [n_points, 3]
    points = pv.pyvista_ndarray(vertices)

    # PyVista espera las caras en formato:
    # [3, v0, v1, v2, 3, v3, v4, v5, ...]
    faces_formatted = []
    for f in faces:
        faces_formatted.append(3)
        faces_formatted.extend(f)
    faces_formatted = pv.pyvista_ndarray(faces_formatted)

    mesh = pv.PolyData(points, faces_formatted)
    mesh.save(filename)
    print(f"STL exportado: {filename}")
