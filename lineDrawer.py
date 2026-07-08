import cv2
import os
import re


# ====================================================
# ESTADO GLOBAL
# ====================================================
points = []

video = ('aquisicao14.dav')

# ====================================================
# CALLBACK DE MOUSE
# ====================================================
def click_event(event, x, y, flags, param):

    global points

    if event == cv2.EVENT_LBUTTONDOWN:

        points.append((x, y))

        # Cria cópia para desenhar feedback
        frame_temp = frame_resized.copy()

        if len(points) == 1:

            # Desenha ponto inicial
            cv2.circle(frame_temp, points[0], 5, (0, 255, 0), -1)
            cv2.imshow("Selecionar Linha (Clique 2 pontos)", frame_temp)

        elif len(points) == 2:

            # Desenha linha final
            cv2.line(frame_temp, points[0], points[1], (0, 0, 255), 2)
            cv2.imshow("Selecionar Linha (Clique 2 pontos)", frame_temp)
            cv2.waitKey(300)

            # Mapeia os pontos de volta para a resolução original do vídeo
            p1 = (int(points[0][0] * orig_w / 1200), int(points[0][1] * orig_h / 800))
            p2 = (int(points[1][0] * orig_w / 1200), int(points[1][1] * orig_h / 800))

            # Atualiza o arquivo TrackerSystem.py
            filepath = os.path.join("MyTrack", "TrackerSystem.py")
            
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            pattern = r"self\.pLine\s*=\s*ParkLine\(.*\)"
            replacement = f"self.pLine = ParkLine({p1}, {p2}, (0, 0, 255), 3)"
            content = re.sub(pattern, replacement, content)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)

            print(f"Linha atualizada com sucesso em: {filepath}")
            print(f"Nova linha: {replacement}")
            
            os._exit(0)


# ====================================================
# PRINCIPAL
# ====================================================
# Abre o vídeo para obter a resolução e o primeiro frame
cap = cv2.VideoCapture(video)
ret, frame = cap.read()
cap.release()

if not ret:
    print("Erro ao ler o frame do vídeo.")
    os._exit(1)

orig_h, orig_w = frame.shape[:2]
frame_resized = cv2.resize(frame, (1200, 800))

# Janela de exibição
cv2.imshow("Selecionar Linha (Clique 2 pontos)", frame_resized)
cv2.setMouseCallback("Selecionar Linha (Clique 2 pontos)", click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()
