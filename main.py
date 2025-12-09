from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np
import base64

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

def processar_grid_tabaco(img_bytes):
    # Decodifica a imagem
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Redimensiona (Grid 10x10 precisa de quadrado)
    # DICA: No futuro, o App deve garantir o corte quadrado.
    # Aqui forçamos 1000x1000 para o grid matemático funcionar.
    img = cv2.resize(img, (1000, 1000))
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    
    # Ajuste para Verde
    lower_green = np.array([30, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv, lower_green, upper_green)
    
    step = 100 # 1000/10
    germinados = 0
    falhas = 0
    
    for i in range(10):
        for j in range(10):
            y1, x1 = i*step, j*step
            y2, x2 = y1+step, x1+step
            roi = mask[y1:y2, x1:x2]
            
            # Se tem mais de 20 pixels verdes (ajustável)
            if cv2.countNonZero(roi) > 20:
                germinados += 1
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            else:
                falhas += 1
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), 2)
                # X vermelho para visualização clara
                cv2.line(img, (x1, y1), (x2, y2), (0, 0, 255), 1)
                cv2.line(img, (x2, y1), (x1, y2), (0, 0, 255), 1)

    # Converte imagem final para Base64
    _, buffer = cv2.imencode('.jpg', img)
    img_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return germinados, falhas, img_base64

@app.post("/analisar")
async def analisar(file: UploadFile = File(...)):
    contents = await file.read()
    germinados, falhas, img_base64 = processar_grid_tabaco(contents)
    return {
        "germinados": germinados,
        "falhas": falhas,
        "imagem": img_base64
    }
