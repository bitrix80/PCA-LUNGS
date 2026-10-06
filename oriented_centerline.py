
import numpy as np
from collections import deque

# ---------------------------------------------------------------------------
# Orient branch point sequences from inlet to tip
# ---------------------------------------------------------------------------
def build_ordered_indices(centerline):
    """
    The VTP cell connectivity is not guaranteed to be ordered inlet->tip.
    Detect the root branch (ParentBranchId == -1), orient it so its end
    connects to its children, then propagate orientation top-down via BFS.
    Returns ordered point-index arrays per branch and the tree structure.
    """
    branch_ids_arr = centerline.cell_data["BranchId"]
    parent_ids_arr = centerline.cell_data["ParentBranchId"]

    # Extract raw (unoriented) point index arrays for each branch
    raw = {}
    for cell_id in range(centerline.n_cells):
        bid  = int(branch_ids_arr[cell_id])
        cell = centerline.get_cell(cell_id)
        raw[bid] = np.array([cell.GetPointId(j) for j in range(cell.n_points)])

    parent_map = {int(branch_ids_arr[i]): int(parent_ids_arr[i])
                  for i in range(centerline.n_cells)}

    root_bid = next(bid for bid, pid in parent_map.items() if pid == -1)

    # Orient root so its last point is closest to its children's start points
    ordered  = {}
    root_idx = raw[root_bid].copy()
    child_bids = [bid for bid, pid in parent_map.items() if pid == root_bid]
    child_refs = []
    for cbid in child_bids:
        cidx = raw[cbid]
        child_refs += [centerline.points[cidx[0]], centerline.points[cidx[-1]]]
        #child_refs += [centerline.points.GetPoint(cidx[0]), centerline.points.GetPoint(cidx[-1])]
    child_refs = np.array(child_refs)

    if len(child_refs) > 0:
        d_start = np.min(np.linalg.norm(child_refs - centerline.points[root_idx[0]],  axis=1))
        d_end   = np.min(np.linalg.norm(child_refs - centerline.points[root_idx[-1]], axis=1))
        #d_start = np.min(np.linalg.norm(child_refs - centerline.points.GetPoint(root_idx[0]),  axis=1))
        #d_end   = np.min(np.linalg.norm(child_refs - centerline.points.GetPoint(root_idx[-1]), axis=1))
        if d_start < d_end:
            root_idx = root_idx[::-1]
    ordered[root_bid] = root_idx

    # BFS: orient each child so its first point connects to its parent's last point
    queue = deque([root_bid])
    while queue:
        pbid       = queue.popleft()
        parent_end = centerline.points[ordered[pbid][-1]]
#        parent_end = np.asarray(centerline.points.GetPoint(ordered[pbid][-1]))
        for cbid in [bid for bid, pid in parent_map.items() if pid == pbid]:
            cidx = raw[cbid].copy()
            #aa = np.asarray(centerline.points.GetPoint(cidx[0]))
            #bb = np.asarray(centerline.points.GetPoint(cidx[-1]))
            d_s  = np.linalg.norm(centerline.points[cidx[0]]  - parent_end)
            d_e  = np.linalg.norm(centerline.points[cidx[-1]] - parent_end)   
            #d_s  = np.linalg.norm(aa - parent_end)
            #d_e  = np.linalg.norm(bb - parent_end)
            if d_e < d_s:
                cidx = cidx[::-1]
            ordered[cbid] = cidx
            queue.append(cbid)

    return ordered, root_bid, parent_map
