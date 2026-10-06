"""


Operacions geomètriques sobre centerlines.

"""

import numpy as np


# ============================================================
# UTILITATS
# ============================================================

def norm(v):
    """Norma euclidiana."""
    return np.linalg.norm(v)


def normalize(v):
    """Vector unitari."""
    n = np.linalg.norm(v)

    if n < 1e-12:
        return np.zeros(3)

    return v / n


# ============================================================
# LONGITUD D'ARC
# ============================================================

def cumulative_lengths(points):
    """
    Longitud acumulada.

    Parameters
    ----------
    points : (N,3)

    Returns
    -------
    s : (N,)
    """

    n = len(points)

    s = np.zeros(n)

    for i in range(1, n):

        ds = norm(points[i] - points[i-1])

        s[i] = s[i-1] + ds

    return s


# ============================================================
# xi -> punt del centerline
# ============================================================

def point_from_xi(points,
                  arc,
                  xi):
    """
    Interpolació lineal.

    xi pertany a [0,1]
    """

    L = arc[-1]

    target = xi * L

    if target <= 0:
        return points[0]

    if target >= L:
        return points[-1]

    i = np.searchsorted(arc, target)

    i0 = i-1
    i1 = i

    s0 = arc[i0]
    s1 = arc[i1]

    t = (target-s0)/(s1-s0)

    return (1-t)*points[i0] + t*points[i1]


# ============================================================
# xi -> vector tangent al centerline en aquest punt xi ---- crec que potser no cal
# ============================================================

def tangent_from_xi(points,
                    arc,
                    xi):

    L = arc[-1]

    target = xi * L

    if target <= 0:

        return normalize(
            points[1]-points[0]
        )

    if target >= L:

        return normalize(
            points[-1]-points[-2]
        )

    i = np.searchsorted(arc, target)

    return normalize(
        points[i]-points[i-1]
    )


# ============================================================
# PROJECCIÓ SOBRE SEGMENT (per projectar un punt x de la STL sobre el centerline)
# ============================================================

def project_on_segment(x,
                       a,
                       b):
    """
    Projecta x sobre el segment ab.
    Returns
    -------
    p
    alpha
    dist
    """
    ab = b-a
    lab2 = np.dot(ab, ab)
    if lab2 < 1e-12:
        return a.copy(), 0.0, norm(x-a)

   #Projecció ortogonal 
    alpha_raw = np.dot(x-a,ab) / lab2
    alpha = np.clip(alpha_raw,0.0,1.0)
    p = a + alpha*ab
    d = norm(x-p)

    return p, alpha, d , alpha_raw  #p és la projecció, alpha és la posició relativa al centerline (utilitzarem per trobar xi), d distància mínima


# ============================================================
# PROJECCIÓ SOBRE BRANCH
# ============================================================
def project_on_branch(x,
                      points,
                      arc):
    """
    Cerca el punt més proper del centerline.
    Retorna
    -------
    xi
    p
    v
    dist
    """

    best_dist = np.inf
    best_p = None
    best_xi = None
    total = arc[-1]

    for i in range(len(points)-1):
        p, alpha, d , alpha_raw  = project_on_segment(
            x,
            points[i],
            points[i+1]
        )
        outside = (alpha_raw < 0 or alpha_raw > 1)
        if d < best_dist:
            best_dist = d
            best_p = p
            s = arc[i]
            ds = alpha * (
                arc[i+1]-arc[i]
            )

            best_xi = (s+ds)/total
   
    v = x-best_p

    return (
        best_xi,
        best_p,
        v,
        best_dist,
        outside
    )


# ============================================================
# TOTES LES BRANQUES --- es queda amb la mínima distància entre projecció a la branch i el punt, entre totes les branches
# ============================================================

def project_on_branches(x,
                        branches,
                        max_distance=None): #poso llindar de distància per no agafar punts del STL d'altres branches
    """
    Parameters
    ----------

    branches

    [
        {
            "id":...
            "points":...
            "arc":...
        },
        ...
    ]

    Returns
    -------
    branch
    xi
    p
    v
    dist
    """
    best = np.inf
    out = None
    for branch in branches:

        xi, p, v, d , outside= project_on_branch(
            x,
            branch["points"],
            branch["arc"]
        )
        if d < best:
            best = d
            out = (
                branch,
                xi,
                p,
                v,
                d,
                outside
            )

    if out is None:
        return None

    branch, xi, p, v, d, outside = out

    if max_distance is not None and d > max_distance:
        return None

    return out


# ============================================================
# REESCALAR LONGITUD
# ============================================================

def rescale_arc(points,
                new_length=10.0):
    """
    Manté la forma però escala
    la longitud total.
    """

    arc = cumulative_lengths(points)

    L = arc[-1]

    if L < 1e-12:
        return points.copy()

    scale = new_length/L

    new_points = [points[0]]

    for i in range(1, len(points)):

        v = points[i]-points[i-1]

        new_points.append(
            new_points[-1] + scale*v
        )

    return np.array(new_points)


# ============================================================
# VECTOR RADIAL UNITARI
# ============================================================

def radial_vector(v):

    return normalize(v)
