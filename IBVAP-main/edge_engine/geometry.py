from typing import Tuple, List, Optional

def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
    if len(polygon) < 3: return False
    x, y = point
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def get_bottom_center(bbox: Tuple[float, float, float, float]) -> Tuple[float, float]:
    x1, y1, x2, y2 = bbox
    return ((x1 + x2) / 2.0, float(y2))

class DirectionalTripwire:
    def __init__(self, p1: Tuple[float, float], p2: Tuple[float, float]):
        self.p1 = p1
        self.p2 = p2

    def check_crossing(self, prev_pos: Tuple[float, float], curr_pos: Tuple[float, float]) -> Optional[str]:
        def cross_product(x, y):
            x1, y1 = self.p1
            x2, y2 = self.p2
            return (x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)

        cp1 = cross_product(*prev_pos)
        cp2 = cross_product(*curr_pos)

        if cp1 * cp2 < 0:
            return 'IN' if cp2 > 0 else 'OUT'
        return None

class PolygonZone:
    def __init__(self, vertices: List[Tuple[float, float]], zone_type: str = 'inclusion'):
        self.vertices = vertices
        self.zone_type = zone_type

    def check_breach(self, point: Tuple[float, float]) -> bool:
        is_inside = point_in_polygon(point, self.vertices)
        if self.zone_type == 'inclusion':
            return not is_inside
        else:
            return is_inside
