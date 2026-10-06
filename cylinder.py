"""


Construeix el centerline dels cilindres associats a les
3 primeres branques.

No construeix la superfície del cilindre.
Només la funció phi_cil(xi).

"""

import numpy as np

from geometry import normalize
from geometry import point_from_xi

# ============================================================
# Calcula la longitud real de la branch
# ============================================================

def branch_length(branch):
    pts = branch["points"]
    return np.sum(np.linalg.norm(pts[1:] - pts[:-1], axis=1))

# ============================================================
# Calcula la distancia real desde el origen de la branch
# ============================================================

def branch_distance(branch, xi):
    pts = branch["points"]
    total = branch_length(branch)
    return xi * total

# ============================================================
# Matriu de rotació --- per girar els cilindres corresponents a les filles en 45 graus (potser no cal)
# ============================================================

def rotation_matrix(axis, angle):

    axis = normalize(axis)

    x, y, z = axis

    c = np.cos(angle)
    s = np.sin(angle)
    C = 1.0 - c

    R = np.array([

        [c+x*x*C,
         x*y*C-z*s,
         x*z*C+y*s],

        [y*x*C+z*s,
         c+y*y*C,
         y*z*C-x*s],

        [z*x*C-y*s,
         z*y*C+x*s,
         c+z*z*C]

    ])

    return R
# ============================================================
# DireccióINVERTIDA d'una branca
# ============================================================


def initial_direction_inverted(branch):
    pts = branch["points"]
    d = pts[1] - pts[0]
    return normalize(-d)   # dirección invertida


# ============================================================
# Direcció inicial d'una branca
# ============================================================

def initial_direction(branch):

    pts = branch["points"]

    d = pts[1]-pts[0]
 # Si la tráquea apunta hacia arriba, la invertimos
 #   if branch["id"] == 89:   # tráquea
 #       if d[2] > 0:         # si Z sube
 #           d = -d
    return normalize(d)


# ============================================================
# Direcció final d'una branca
# ============================================================

def final_direction(branch):

    pts = branch["points"]

    d = pts[-1]-pts[-2]

    return normalize(d)


# ============================================================
# Classe CylinderBranch
# ============================================================

class CylinderBranch:

#Creació del cilindre (de la seva centerline)

    def __init__(self,
                 origin,
                 direction,
                 length=10.0,
                 branch_id=None):

        self.origin = origin.copy()

        self.direction = normalize(direction)

        self.length = length

        self.id = branch_id
    # phi_cil(xi)

    def point(self, xi):

        xi = np.clip(xi,0.0,1.0)

        return self.origin + xi*self.length*self.direction

    def project(self, x):
        o = self.origin
        u = self.direction
        L = self.length

        xi = np.dot(x - o, u) / L
        if np.allclose(x, [6.1672187,9.151931,93.95511]):
            print("en project del cilindro-o", o)
            print("en project del cilindro-u", u)
            print("en project del cilindro-L", L)
            print("en project del cilindro-xi", xi)
        xi = np.clip(xi, 0.0, 1.0)

        return xi   


# ============================================================
# Branca principal, construcció cilindre corresponent
# ============================================================
def root_cylinder(branch, origin_common):
    direction = initial_direction(branch)
    return CylinderBranch(origin_common, direction, 10.0, branch["id"])

#def root_cylinder(root):

#    origin = root["points"][0]

#    direction = initial_direction(root)
    
#    branch_id = root["id"]  

#    return CylinderBranch(
#        origin,
#        direction,
#        10.0,
#        branch_id = branch_id
#    )


# ============================================================
# Filla, construcció cilindre corresponent
# ============================================================
def child_cylinder(branch, origin_common):
    direction = initial_direction_inverted(branch)
    return CylinderBranch(origin_common, direction, 10.0, branch["id"])


#def child_cylinder(parent_cyl, branch):

    # El origen del hijo es el final del cilindro padre
#    origin = parent_cyl.origin + parent_cyl.direction * parent_cyl.length

    # Dirección real de la branch, pero recalculada desde el origen artificial
    #pts = branch["points"]
    #d = pts[1] - origin
    #direction = normalize(d)

    # La dirección del hijo sigue la banch
#    direction = initial_direction(branch)

#    branch_id = branch["id"]

#    return CylinderBranch(origin, direction, 10.0, branch_id)



#def child_cylinder(parent_cylinder,
#                   child_branch):
#
#   """
#    El cilindre comença exactament
#    al final del cilindre pare.
#
#    La seva orientació és la mateixa
#    que la branca original.
#    """

#    origin = parent_cylinder.point(1.0) #final cilindre pare

#    direction = normalize(   #mateixa direcció que la branca original del centerline
#        child_branch["points"][-1]
#        -
#        child_branch["points"][0]
#    )
    
#    branch_id = branch["id"] 

#    return CylinderBranch(
#        origin,
#        direction,
#        10.0,
#        branch_id = branch_id
#
#    )


# ============================================================
# Construcció dels tres cilindres
# ============================================================

def first_three_cylinders(branches):
    # Punto inicial de la tráquea
    origin_root= branches[0]["points"][0]
       
    # Punto de bifurcación real
    bif = branches[0]["points"][-1] 

    # Dirección REAL hacia la bifurcación
    direction_root = (bif - origin_root)
    direction_root /= np.linalg.norm(direction_root)
    # Cilindro raíz: desde la tráquea hasta la bifurcación
    cyl_root = CylinderBranch(
        origin_root,
        direction_root,
        10.0,
        branches[0]["id"]
    )
    # Hijos
    #direction_child1 = normalize(branches[1]["points"][1] - bif)
    #direction_child2 = normalize(branches[2]["points"][1] - bif)

    # ========================================================
    # LOS HIJOS NACEN DEL FINAL DEL PADRE
    # ========================================================

    child_origin = cyl_root.point(1.0)

    direction_child1 = normalize(
        branches[1]["points"][1] - branches[1]["points"][0]
    )

    direction_child2 = normalize(
        branches[2]["points"][1] - branches[2]["points"][0]
    )

    """
    # Cilindro hijo 1: desde la bifurcación hacia su rama
    cyl_child1 = CylinderBranch(
        bif,
        direction_child1,
        10.0,
        branches[1]["id"]
    )

    # Cilindro hijo 2: desde la bifurcación hacia su rama
    cyl_child2 = CylinderBranch(
        bif,
        direction_child2,
        10.0,
        branches[2]["id"]
    )

    """

    cyl_child1 = CylinderBranch(
        child_origin,
        direction_child1,
        10.0,
        branches[1]["id"]
    )

    cyl_child2 = CylinderBranch(
        child_origin,
        direction_child2,
        10.0,
        branches[2]["id"]
    )



    #cyl_root = root_cylinder(branches[0], origin_common)

    #cyl_child1 = child_cylinder(branches[1],origin_common)
    #cyl_child2 = child_cylinder(branches[2],origin_common)
###cyl_child2 = child_cylinder(cyl_child1, branches[2])

    return [cyl_root, cyl_child1, cyl_child2]




#def first_three_cylinders(branches):
#
#    """
#    branches[0] = arrel
#
#    branches[1] = filla
#
#    branches[2] = filla
#    """
#
#    cyl_root = root_cylinder(
#        branches[0]
#    )
#
#    cyl_child1 = child_cylinder(
#        cyl_root,
#        branches[1]
#    )
#
#    cyl_child2 = child_cylinder(
#        cyl_root,
#        branches[2]
#    )
#
#    return [
#
#        cyl_root,
#
#        cyl_child1,
#
#        cyl_child2
#
#    ]



# ============================================================
# Cercar el cilindre associat a una branca
# ============================================================

"""""
def cylinder_from_branch(branch,
                         branches,
                         cylinders):
"""
    #Retorna el cilindre corresponent a una branca.
"""

    branch_id = branch["id"]

    for b, cyl in zip(branches, cylinders):

        if b["id"] == branch_id:
            return cyl

    raise RuntimeError(
        f"No s'ha trobat el cilindre de la branca {branch_id}"
    )

"""""
# ============================================================
# Phi_cil(xi)
# ============================================================

"""
def phi_cylinder(branch,
                 xi,
                 branches,
                 cylinders):
"""
"""
    Punt del centerline del cilindre corresponent.

    Parameters
    ----------
    branch : branca original

    xi : paràmetre longitudinal [0,1]

    Returns
    -------
    np.ndarray (3,)
"""
"""
    cyl = cylinder_from_branch(
        branch,
        branches,
        cylinders
    )

    return cyl.point(xi)

"""
# ============================================================
# Transport radial
# ============================================================

def map_point_to_cylinder(branch,
                          xi,
                          projection_vector,
                          branches,
                          cylinders):
    """
    Implementa:

        phi_cil(xi) + v_perp / ||v_perp||
    """

    # Encontrar cilindro por ID (sin zip)
    cyl = None
    for c in cylinders:
        if c.id == branch["id"]:
            cyl = c
            break

    if cyl is None:
        raise RuntimeError(
            f"No existe cilindro para la branch {branch['id']}"
        )

    # Punto del eje del cilindro
    center = cyl.point(xi)

    # Dirección del cilindro
    u = cyl.direction

    # Vector original desde la geometría real
    v = projection_vector

    # Descomposición en paralelo + perpendicular
    v_parallel = np.dot(v, u) * u
    v_perp = v - v_parallel

    # Si la dirección del cilindro está invertida,
    # el radial también debe invertirse.
    # (IDs de tus dos hijos) OJOOO!
    #if cyl.id in [52, 60]:
    #if cyl.id in [89]:
    #   v_perp = -v_perp

    # Normalización
    n = np.linalg.norm(v_perp)
    if n < 1e-12:
        return center.copy()

    radial = v_perp / n

    return center + radial


#def map_point_to_cylinder(branch,
#                          xi,
#                          projection_vector,
#                          branches,
#                          cylinders):
#    """
#    Implementa
#
#        phi_cil(xi) + v/||v||
#    """
#
#    # Busquem quin cilindre correspon a aquesta branca
#    cyl = None
#
#    for c in cylinders:
#        if c.id == branch["id"]:
#            cyl = c
#            break
#
#        #for b, c in zip(branches, cylinders):
#
#        #if b["id"] == branch["id"]:
#        #    cyl = c
#        #    break
#
#     if cyl is None:
#        raise RuntimeError(
#            f"No existeix cap cilindre per a la branca {branch['id']}"
#        )
#
#    # Punt del centerline del cilindre
#    center = cyl.point(xi)
#
#    u = cyl.direction
#
#    v = projection_vector
#
#    v_parallel = np.dot(v, u) * u
#
#    v_perp = v - v_parallel
#
#    n = np.linalg.norm(v_perp)
#
#    if n < 1e-12:
#        return center.copy()
#
#    radial = v_perp / n
#
#    return center + radial



# ============================================================
# Test
# ============================================================

if __name__ == "__main__":

    from centerline import first_three_branches


    cylinders = first_three_cylinders(branches)

    print()

    for i, cyl in enumerate(cylinders):

        print("----------------------------------")
        print("Cilindre", i)
        print("----------------------------------")

        print("Origen     :", cyl.origin)
        print("Direcció   :", cyl.direction)
        print("Longitud   :", cyl.length)

        print("phi(0.0)   :", cyl.point(0.0))
        print("phi(0.5)   :", cyl.point(0.5))
        print("phi(1.0)   :", cyl.point(1.0))

