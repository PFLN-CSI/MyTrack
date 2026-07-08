from typing import Dict, Optional, Tuple
import math

from Car import Car


class CarManager:

    def __init__(self):

        self.cars: Dict[int, Car] = {}

        # REAL ID -> VIRTUAL ID
        self.real_to_virtual: Dict[int, int] = {}

        self.next_virtual_id = 1

        self.reid_distance = 120

        # evita criar dois carros praticamente no mesmo lugar
        self.same_car_distance = 40

    # ====================================================
    # DISTÂNCIA
    # ====================================================
    def _distance(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return math.hypot(a[0] - b[0], a[1] - b[1])

    # ====================================================
    # CRIA CARRO
    # ====================================================
    def create_car(self, real_id: int, center: Tuple[int, int], frame: int, vehicle_type: str, status: str):

        car = Car(
            virtual_id=self.next_virtual_id,
            real_id=real_id,
            center=center,
            frame=frame,
            vehicle_type=vehicle_type,
            status = status
        )
        self.cars[self.next_virtual_id] = car
        self.real_to_virtual[real_id] = self.next_virtual_id

        print("\n" + "=" * 70)
        print("NOVO CARRO CRIADO")
        print("=" * 70)
        print(f"Virtual ID : {car.virtual_id}")
        print(f"Real ID    : {real_id}")
        print(f"Posição    : ({center[0]}, {center[1]})")
        print(f"Frame      : {frame}")
        print(f"Type       : {vehicle_type}")
        print("=" * 70)


        print("\nCARROS CADASTRADOS")

        for car in self.cars.values():
            print(
                f"VID:{car.virtual_id:03d}  "
                f"REAL:{car.get_real_id():03d}  "
                f"POS:{car.get_position()}  "
                f"TIPO:{car.get_vehicle_type()}"
            )

        print(" Ultimo "+str(self.next_virtual_id))        
        self.next_virtual_id += 1
        print(" Proximo "+str(self.next_virtual_id))        

        return car

    # ====================================================
    # GET POR REAL ID
    # ====================================================
    def get_by_real_id(self, real_id: int, status:str):

        vid = self.real_to_virtual.get(real_id)

        if vid is None :
            return None
        if self.cars.get(vid).get_status()!=status:
            print("Status Diferente")
            return None

        return self.cars.get(vid)

    

    # ==================================================== 
    #  PROCURA CARRO PERDIDO 
    # ==================================================== 
    
    def find_nearest_lost_car(self, center): 
        best_car = None 
        best_dist = float("inf") 

        for car in self.cars.values(): 
            if car.is_visible(): 
                continue 

            dist = self._distance(car.get_position(), center) 
            print("Distancia "+str(dist)+"  VID"+str(car.get_virtual_id())+ "ID"+str(car.get_real_id()))
            if dist < best_dist and dist < self.reid_distance: 
                best_car = car 
                best_dist = dist 

        return best_car
    
    # ====================================================
    # PROCURA CARRO VISÍVEL PRÓXIMO (ByteTrack duplicou)
    # ====================================================
    def find_nearest_visible_car(
        self,
        center,
        vehicle_type
    ):

        best_car = None
        best_dist = float("inf")

        for car in self.cars.values():

            if not car.is_visible():
                continue
        
            dist = self._distance(
                car.get_position(),
                center
            )

            if dist < best_dist and dist < self.same_car_distance:

                best_car = car
                best_dist = dist

        return best_car

    # ====================================================
    # RE-IDENTIFICA OU CRIA
    # ====================================================
    def reidentify_or_create(
        self,
        real_id: int,
        center: Tuple[int, int],
        frame: int,
        vehicle_type : str,
        status :str
    ):
        
        # ----------------------------------------
        # 1 - TrackID já conhecido
        # ----------------------------------------

        car = self.get_by_real_id(real_id,status)

        if car:

            car.update(
                real_id,
                center,
                frame,
                vehicle_type,
                status
            )

            car.set_visible(True)
            #print(" Atualizou "+str(car.get_virtual_id()))
            return 1, car

        # ----------------------------------------
        # 2 - Recupera carro perdido
        # ----------------------------------------

        car = self.find_nearest_lost_car(center)

        if car is not None:

            print(f"Recuperou  REAL:{real_id} -> VID:{car.get_virtual_id()}")

            car.update(
                real_id,
                center,
                frame,
                vehicle_type,
                status
            )

            self.real_to_virtual[real_id] = car.get_virtual_id()

            car.set_visible(True)
            print(" Recuperou "+str(car.get_virtual_id()))
            return 2, car

        # ----------------------------------------
        # 3 - ByteTrack criou outro Track
        #     para o mesmo carro
        # ----------------------------------------

        car = self.find_nearest_visible_car(
            center,
            vehicle_type
        )

        if car is not None:

            print(f"DUPLICADO  REAL:{real_id} -> VID:{car.get_virtual_id()}")

            self.real_to_virtual[real_id] = car.get_virtual_id()

            car.update(
                real_id,
                center,
                frame,
                vehicle_type,
                status
            )
            print(status+" Duplicado "+str(car.get_virtual_id()))
            return 3, car

        # ----------------------------------------
        # 4 - É realmente um carro novo
        # ----------------------------------------
        o_car=self.create_car(
            real_id,
            center,
            frame,
            vehicle_type,
            status
        )
        print(status+" Novo Carro "+str(o_car.get_virtual_id()))
        return 4, o_car

    # ====================================================
    # FRAME RESET
    # ====================================================
    def start_frame(self):

        for car in self.cars.values():
            car.set_visible(False)

    # ====================================================
    # DEBUG
    # ====================================================
    def print_all(self):

        print("\n" + "=" * 60)

        for car in self.cars.values():

            print(
                f"VID:{car.virtual_id:03d} "
                f"REAL:{car.get_real_id():03d} "
                f"VISIBLE:{car.visible} "
                f"POS:{car.get_position()}"
            )

        print("=" * 60 + "\n")