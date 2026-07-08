import cv2
import time
import json
import os
from ultralytics import YOLO

from ParkLine import ParkLine
from CarManager import CarManager


START_TIME_SECONDS = 1


class TrackerSystem:

    def __init__(self):

        # =========================
        # MODELO
        # =========================
        self.model = YOLO("yolov8m.pt")
       
        # =========================
        # SISTEMAS
        # =========================
        self.pLine = None
        self.car_manager = CarManager()

        # =========================
        # VÍDEO
        # =========================
        self.cap = cv2.VideoCapture("v10.mp4")
        #self.cap = cv2.VideoCapture("v10.mp4")
        self.cap.set(cv2.CAP_PROP_POS_MSEC, START_TIME_SECONDS * 1000)

        # =========================
        # ESTADO GLOBAL
        # =========================
        self.frame_count = 0
        self.start_time = time.time()

        self.logs = {}
        self.pause_requested = False

        self.LOG_DIR = "Logs"
        os.makedirs(self.LOG_DIR, exist_ok=True)

    # ====================================================
    # CONFIGURA LINHAS
    # ====================================================
    def setup_lines(self):

        self.pLine = ParkLine((2667, 1085), (77, 352), (0, 0, 255), 3)
       
   
    # ====================================================
    # LOOP PRINCIPAL
    # ====================================================
    def run(self):

        self.setup_lines()

        SKIP_FRAMES = 1

        while True:

            ret, frame = self.cap.read()
            if not ret:
                break

            self.frame_count += 1

            if self.frame_count % SKIP_FRAMES != 0:
                continue

            # =========================
            # YOLO TRACK
            # =========================
            results = self.model.track(
                frame,
                persist=True,
                conf=0.3,                
                classes=[2, 7],
                tracker="meu_bytetrack.yaml",
                verbose=False,
                device=0,  
            )

            # =========================
            # FPS
            # =========================
            elapsed = time.time() - self.start_time
            fps = self.frame_count / elapsed if elapsed > 0 else 0
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            # =========================
            # RESET VISIBILIDADE
            # =========================
            self.car_manager.start_frame()

            # =========================
            # PROCESSAMENTO DETECÇÕES
            # =========================
            for result in results:

                if result.boxes is None:
                    continue

                for box in result.boxes:

                    if box.id is None:
                        continue

                    # -------------------------
                    # BBOX
                    # -------------------------
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    track_id = int(box.id[0])
                    conf = float(box.conf[0])
                    classe = int(box.cls[0])

                    cx = (x1 + x2) // 2
                    cy = (y1 + y2) // 2

                    # -------------------------
                    # LINHAS
                    # -------------------------
                    analysis = self.pLine.evaluate_bbox(x1, y1, x2, y2)              
                    print(analysis)
                    signed_distance = analysis["signed_distance"]                    
                    side = analysis["side"]
                    dist = analysis["distance"]

                    if signed_distance > 30:
                        status = "andando"
                    elif signed_distance < -30:
                        status = "estacionado"
                    else:                       
                        status = "indefinido"

                    status="andando" if side > 0 else "estacionado"
                    # -------------------------
                    # CAR MANAGER (RE-ID + CREATE)
                    # -------------------------
                    vehicle_type = self.model.names[classe]
                    tipo, car = self.car_manager.reidentify_or_create(
                        track_id,
                        (cx, cy),
                        self.frame_count,
                        vehicle_type,
                        status
                    )
                    if (tipo==4):
                        self.pause_requested = True
                                      
                    # -------------------------
                    # COR VISUAL
                    # -------------------------
                    color = (0, 0, 255) if side > 0 else (255, 0, 0)

                    # -------------------------
                    # LABEL
                    # -------------------------
                    label = f"VID:{car.virtual_id} ID:{track_id} {conf:.2f}"

                    # -------------------------
                    # LOG
                    # -------------------------
                    self.logs.setdefault(track_id, []).append({
                        "frame": self.frame_count,
                        "time": timestamp,
                        "track_id": track_id,
                        "virtual_id": car.virtual_id,
                        "center": {"x": cx, "y": cy},
                        "side": float(side),
                        "distance": float(dist),
                        "fps": fps
                    })

                    # -------------------------
                    # DRAW BOX
                    # -------------------------
                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)

                    cv2.putText(
                        frame,
                        label,
                        (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.6,
                        color,
                        2
                    )

            # =========================
            # DESENHAR LINHA
            # =========================
            
            line =  self.pLine

            cv2.line(
                    frame,
                    (line.x1, line.y1),
                    (line.x2, line.y2),
                    line.color,
                    line.thickness
                )

            # =========================
            # DISPLAY
            # =========================
            frame = cv2.resize(frame, (1200, 800))
            cv2.imshow("TrackerSystem", frame)

            if self.pause_requested:

                print("Pressione C para continuar...")

                while True:

                    key = cv2.waitKey(0) & 0xFF

                    if key in (ord('c'), ord('C')):
                        self.pause_requested = False
                        break

                    if key == 27:
                        return

            if cv2.waitKey(1) & 0xFF == 27:
                break

        
        self.cap.release()
        cv2.destroyAllWindows()

