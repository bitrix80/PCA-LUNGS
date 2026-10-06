import vtk
import numpy as np

def exportar_caras_mezcladas_vtp(vertices,
                                 faces,
                                 xis_centerline,
                                 xis_cilindro,
                                 caras_mezcladas,
                                 filename="caras_mezcladas.vtp"):

    # --- Crear estructura PolyData ---
    poly = vtk.vtkPolyData()

    # --- Puntos ---
    vtk_points = vtk.vtkPoints()
    for x, y, z in vertices:
        vtk_points.InsertNextPoint(float(x), float(y), float(z))
    poly.SetPoints(vtk_points)

    # --- Caras mezcladas como celdas ---
    vtk_cells = vtk.vtkCellArray()    
    mezclada_arr = vtk.vtkIntArray()
    mezclada_arr.SetName("mezclada")

    caras_validas = [] 
    for cara in caras_mezcladas:

        # Caso 1: cara es un índice entero
        if isinstance(cara, int):
            tri = faces[cara]

        # Caso 2: cara es tupla/lista de vértices
        elif isinstance(cara, (tuple, list)) and len(cara) == 2 and isinstance(cara[0], int):
            tri = faces[cara[0]]
        
        # Caso 3: cara es ya un triángulo
        elif isinstance(cara, (tuple, list)) and len(cara) == 3:
            tri = cara

        # Caso 3: cara híbrid ignorar
        else:
            print(f"Ignorando cara rara: {cara}")
            continue

        # Crear triángulo
        cell = vtk.vtkTriangle()
        cell.GetPointIds().SetId(0, int(tri[0]))
        cell.GetPointIds().SetId(1, int(tri[1]))
        cell.GetPointIds().SetId(2, int(tri[2]))
        vtk_cells.InsertNextCell(cell)
        
         # Campo booleano mezclada = 1
        mezclada_arr.InsertNextValue(1)

    poly.SetPolys(vtk_cells)

    # --- xi_centerline ---
    xi_center_arr = vtk.vtkFloatArray()
    xi_center_arr.SetName("xi_centerline")
    for val in xis_centerline:
        xi_center_arr.InsertNextValue(float(val))
    poly.GetPointData().AddArray(xi_center_arr)

    # --- xi_cilindro ---
    xi_cil_arr = vtk.vtkFloatArray()
    xi_cil_arr.SetName("xi_cilindro")
    for val in xis_cilindro:
        xi_cil_arr.InsertNextValue(float(val))
    poly.GetPointData().AddArray(xi_cil_arr)

    # --- Guardar ---
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetFileName(filename)
    writer.SetInputData(poly)
    writer.Write()

    print(f"Archivo guardado: {filename}")



