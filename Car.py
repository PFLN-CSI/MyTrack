from collections import deque
from typing import List, Tuple
import math

class Car:

    def __init__(self,virtual_id: int, real_id: int,center: Tuple[int, int], frame: int, vehicle_type: str, status:str):

        
        # Identificação        
        self.virtual_id = virtual_id
        # Um carro pode receber vários IDs do tracker
        self.real_ids: List[int] = [real_id]
        # Histórico de posições
        self.positions = deque(maxlen=5)
        self.positions.append(center)
        # Bounding Box
        self.last_bbox = None
        # Estado
        self.status = status
        self.visible = True
        # Tempo
        self.created_frame = frame
        self.last_seen_frame = frame
        # Velocidade
        self.speed = 0.0
        # Linha atual
        self.current_line = None
        # Último lado da linha
        self.line_sides = {}
        # Tipo 
        self.vehicle_type = vehicle_type

        # -----------------------------
        # Dados livres
        # -----------------------------
        self.data = {}

    

    def update(self, real_id: int, center: tuple, frame: int, vehicle_type: str, status: str ):
        if real_id not in self.real_ids:
            self.real_ids.append(real_id)
        self.positions.append(center)
        self.last_seen_frame = frame
        self.visible = True
        self.vehicle_type = vehicle_type
        self.status = status


    def set_bbox(self, bbox):
        self.last_bbox = bbox


    def get_position(self):
        return self.positions[-1]
    

    def get_positions(self):
        return list(self.positions)    

    def get_vehicle_type(self):
        return self.vehicle_type

    def get_real_id(self):
        return self.real_ids[-1]
    
    def get_virtual_id(self):
        return self.virtual_id
    

    def distance_to(self, point):
        x1, y1 = self.get_position()
        x2, y2 = point
        return math.hypot(x2 - x1, y2 - y1)
    

    def set_line_side(self, line_name, side):
        self.line_sides[line_name] = side


    def get_line_side(self, line_name):
        return self.line_sides.get(line_name)
    
    def get_status(self):
        return self.status

    def set_status(self, status):
        self.status = status


    def set_visible(self, visible):
        self.visible = visible


    def is_visible(self):
        return self.visible