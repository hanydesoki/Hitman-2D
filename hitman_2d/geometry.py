def orientation(px: float, py: float, qx: float, qy: float, rx: float, ry: float) -> int:
    """
    Get orientiation of 3 points (P, Q, R).
    Return :
    0 : colinear
    1 : clockwise
    2 : counter-clockwise
    """
    val = (qy - py) * (rx - qx) - (qx - px) * (ry - qy)
    if val == 0:
        return 0
    return 1 if val > 0 else 2

def on_segment(px: float, py: float, qx: float, qy: float, rx: float, ry: float) -> bool:
    """Check if Q point inside PR"""
    return (qx <= max(px, rx) and qx >= min(px, rx) and
            qy <= max(py, ry) and qy >= min(py, ry))

def segments_intersect(x1: float, y1: float, x2: float, y2: float, 
                       x3: float, y3: float, x4: float, y4: float) -> bool:
    """
    Check if segment (x1, y1)-(x2, y2) intersect with (x3, y3)-(x4, y4).
    """
    # Get 4 necessary orientations
    o1 = orientation(x1, y1, x2, y2, x3, y3)
    o2 = orientation(x1, y1, x2, y2, x4, y4)
    o3 = orientation(x3, y3, x4, y4, x1, y1)
    o4 = orientation(x3, y3, x4, y4, x2, y2)

    # General case of intersection
    if o1 != o2 and o3 != o4:
        return True

    # Edge caase (Colinear point on segment)
    if o1 == 0 and on_segment(x1, y1, x3, y3, x2, y2): return True
    if o2 == 0 and on_segment(x1, y1, x4, y4, x2, y2): return True
    if o3 == 0 and on_segment(x3, y3, x1, y1, x4, y4): return True
    if o4 == 0 and on_segment(x3, y3, x2, y2, x4, y4): return True

    return False

