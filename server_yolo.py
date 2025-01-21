import socket
import cv2
import os

from ultralytics import YOLO
from shapely.geometry import Point, Polygon

from time import time

HOST = "127.0.0.1"
PORT = 5959

def yolo_process():
    
    
    rectangle = Polygon([(358,828),(398,726),(1618,718),(1648,816)])   # 다각형 범위 설정.
    
    ################################### CCTV 촬영 코드 ########################################
    # RTSP 스트림 연결
    rtsp_url = "rtsp://admin:pineit0401!@@192.168.0.72:554/profile1/media.smp"
    cap = cv2.VideoCapture(rtsp_url)

    ### 디버깅
    if not cap.isOpened():
        print("RTSP 스트림 연결 실패")
        result_label = 3
        exit()      
    
    ret, frame = cap.read()
    if not ret:     # ret : 프레임 확인 변수
        print("프레임을 읽을 수 없습니다.")
        result_label = 4
        cap.release()
        exit()  
    
    # 원본 이미지 저장
    original_image_folder = "original_images"
    os.makedirs(original_image_folder, exist_ok=True)
    
    time_num = int(time())
    original_image_path = os.path.join(original_image_folder, f"origin_{time_num}.jpg")
    cv2.imwrite(original_image_path, frame)     # (파일이름, 이미지)
    print(f"원본 이미지 저장: {original_image_path}")
    
    ################################## YOLO 예측 코드 ########################################  
    model = YOLO("runs/detect/train43/weights/best.pt") # 모델경로
    results = model(frame, imgsz=320, conf=0.5)

    all_pass = True  # 객체 모두 통과 여부

    for result in results:
        boxes = result.boxes  # results의 BoundingBox 객체

        for box in boxes:  # boxes : 바운딩 박스 객체의 리스트
            
            # 좌표찾기
            coords = box.xyxy[0].tolist()  # xyxy : yolo 바운딩 박스 좌표 [0]: 첫 값만 사용 .tolist() : 리스트로 변환
            x1, y1, x2, y2 = coords  # xyxy 순서
            mid_x = (x1 + x2) / 2
            mid_y = y2  # 아래쪽 y

            # 바운더리 안에 들어왔는지 판별
            point = Point(mid_x, mid_y) # point 객체 생성성
            if not rectangle.contains(point):
                all_pass = False
                color = (0, 0, 255)  #### 빨간색
            else:
                color = (0, 255, 0)  #### 초록색
        
            #### (시각화)바운딩 박스 그리기
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)

            #### (시각화)중간 지점 포인트 그리기
            cv2.circle(frame, (int(mid_x), int(mid_y)), radius=5, color=color, thickness=-1)

        # 결과 출력 # 통과 :1, 실패 :0
        result_label = 1 if all_pass else 0
        print(f"Result: {result_label}")

    # 결과 이미지 저장
    output_folder = "output_img"
    os.makedirs(output_folder, exist_ok=True)
    
    
    output_image_path = os.path.join(output_folder, f"output_{time_num}.jpg")
    cv2.imwrite(output_image_path, frame)
    print(f"결과 이미지 저장: {output_image_path}")

    # 화면에 결과 이미지 표시(선택적)
    cv2.imshow('Result Image', frame)
    cv2.waitKey(0)

    # 자원 해제
    cap.release()
    cv2.destroyAllWindows()
    
    return result_label

###################################################################################3

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"서버가 listen중입니다 {HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept() # conn : 클라이언트와 통신할 소켓, addr : 클라이언트 주소
        print(f"클라이언트 {addr}가 연결되었습니다.")
        data = conn.recv(1024) # 데이터 수신
        
        if data == b"start":
            result_label = yolo_process()
            conn.sendall(str(result_label).encode()) # 결과 전송
        
        elif data == b"end":
            print("서버를 종료합니다.")
            conn.sendall(b"server is terminated") #디코딩 안한상태.
            conn.close()
            break
        
        else:
            print("잘못된 명령입니다.")
        
        conn.close()
            
            