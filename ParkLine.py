import math
from typing import Tuple

Point = Tuple[int, int]
Color = Tuple[int, int, int]


class ParkLine:

    def __init__(self,p1: Point,p2: Point, color: Color = (0, 0, 255),thickness: int = 2):

        self.x1, self.y1 = p1
        self.x2, self.y2 = p2

        self.color = color
        self.thickness = thickness

        self.dx = self.x2 - self.x1
        self.dy = self.y2 - self.y1

        self.length = math.hypot(self.dx, self.dy)

    # =====================================================
    # Distância assinada
    # =====================================================
    def signed_distance(self, x: int, y: int) -> float:

        cross = (
            self.dx * (y - self.y1)
            - self.dy * (x - self.x1)
        )

        if self.length == 0:
            return 0.0

        return cross / self.length

    # =====================================================
    # Lado da linha
    # =====================================================
    def side_of_point(self, x: int, y: int) -> int:

        d = self.signed_distance(x, y)

        if d > 0:
            return 1

        if d < 0:
            return -1

        return 0

    # =====================================================
    # Distância absoluta
    # =====================================================
    def distance_to_point(self, x: int, y: int) -> float:

        return abs(self.signed_distance(x, y))

    # =====================================================
    # Bounding Box
    # =====================================================
    def evaluate_bbox(self, x1, y1, x2, y2):

        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2

        signed = self.signed_distance(cx, cy)

        return {

            "center": (cx, cy),

            # mantém compatibilidade
            "side": 1 if signed > 0 else -1 if signed < 0 else 0,

            "distance": abs(signed),

            # novo campo
            "signed_distance": signed
        }

    # =====================================================
    # Estilo
    # =====================================================
    def get_style(self):

        return {
            "color": self.color,
            "thickness": self.thickness
        }

    # =====================================================
    # Serialização
    # =====================================================
    def to_dict(self):

        return {
            "p1": (self.x1, self.y1),
            "p2": (self.x2, self.y2),
            "color": self.color,
            "thickness": self.thickness
        }
    

    #---------------------------------------------------
    def _evaluate(self, obj, x1, y1, x2, y2):

        line = obj["line"]

        r = self.evaluate_bbox(x1, y1, x2, y2)

        return {
            "name": obj["name"],
            "center": r["center"],
            "side": r["side"],
            "distance": r["distance"],
            "signed_distance": r["signed_distance"],   # <-- adicionar
            "color": line.color,
            "thickness": line.thickness,
            "p1": (line.x1, line.y1),
            "p2": (line.x2, line.y2),
        }

   