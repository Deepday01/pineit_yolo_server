import cv2
import socket
import os

from time import time

HOST = "127.0.0.1"
PORT = 5959


def camera_process():
    
    rtsp_url = "rtsp://admin:pineit0401!@@192.168.0.72:554/profile1/media.smp"
    cap = cv2.VideoCapture(rtsp_url)
    
    if not cap.isOpened():
        print("RTSP 스트림 연결 실패")
        exit()
        
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        cap.release()
        exit()
        
    original_image_folder = "original_images"
    os.makedirs(original_image_folder, exist_ok=True)
    
    original_image_path = os.path.join(original_image_folder, f"{int(time())}.jpg")
    cv2.imwrite(original_image_path, frame)
    print(f"원본 이미지 저장: {original_image_path}")
    
    
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"서버가 listen중입니다. 서버주소:{HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept()
        print(f"클라이언트가 accept되었습니다. 클라이언트 주소:{addr}")
        data = conn.recv(1024)
        
        if data == b"start":
            print("사진 촬영")
            camera_process()
            conn.sendall(str(111).encode()) # 결과 전송

        elif data == b"end":
            print("서버를 종료합니다.")
            conn.sendall(b"server is terminated") #디코딩 안한상태.
            conn.close()
            break
        
        else:
            print("잘못된 명령입니다.")
        
        conn.close()