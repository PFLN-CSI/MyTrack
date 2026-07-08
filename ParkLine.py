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

         

   