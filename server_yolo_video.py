import socket
import cv2
import os
from ultralytics import YOLO
from shapely.geometry import Point, Polygon
from time import time

HOST = "127.0.0.1"
PORT = 5959

def yolo_process():
    rectangle = Polygon([(358, 828), (398, 726), (1618, 718), (1648, 816)])  # 다각형 범위 설정
    
    ################################### CCTV 촬영 코드 ########################################
    rtsp_url = "rtsp://admin:pineit0401!@@192.168.0.72:554/profile1/media.smp"
    cap = cv2.VideoCapture(rtsp_url)

    # 디버깅: RTSP 연결 확인
    if not cap.isOpened():
        print("RTSP 스트림 연결 실패")
        return 3  # 에러 코드

    # 영상 저장 설정
    fps = int(cap.get(cv2.CAP_PROP_FPS))  # FPS (프레임 속도)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))  # 프레임 너비
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))  # 프레임 높이
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")  # 영상 코덱 설정 (MP4)
    
    time_num = int(time())
    output_folder = "output_videos"
    os.makedirs(output_folder, exist_ok=True)
    output_video_path = os.path.join(output_folder, f"output_{time_num}.mp4")
    
    video_writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))
    print(f"결과 영상 저장: {output_video_path}")

    start_time = time()
    all_pass = True  # 모든 객체가 통과했는지 여부
    result_label = 1  # 초기 값 설정

    while True:
        ret, frame = cap.read()
        if not ret:
            print("프레임을 읽을 수 없습니다.")
            break

        # YOLO 예측
        model = YOLO("runs/detect/train43/weights/best.pt")  # 모델 경로
        results = model(frame, imgsz=320, conf=0.5)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                coords = box.xyxy[0].tolist()  # 바운딩 박스 좌표
                x1, y1, x2, y2 = coords
                mid_x = (x1 + x2) / 2
                mid_y = y2

                # 다각형 내 포함 여부 확인
                point = Point(mid_x, mid_y)
                if not rectangle.contains(point):
                    all_pass = False
                    color = (0, 0, 255)  # 빨간색
                else:
                    color = (0, 255, 0)  # 초록색

                # 바운딩 박스 및 포인트 시각화
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                cv2.circle(frame, (int(mid_x), int(mid_y)), radius=5, color=color, thickness=-1)

        # 결과 저장
        video_writer.write(frame)

        # 10초 동안 촬영 후 종료
        if time() - start_time > 10:
            break

    # 자원 해제
    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()

    # 결과 코드 반환 (1: 성공, 0: 실패)
    result_label = 1 if all_pass else 0
    return result_label

###################################################################################

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
    server.bind((HOST, PORT))
    server.listen()
    print(f"서버가 listen 중입니다 {HOST}:{PORT}")
    
    while True:
        conn, addr = server.accept()  # 클라이언트 연결
        print(f"클라이언트 {addr}가 연결되었습니다.")
        data = conn.recv(1024)  # 데이터 수신
        
        if data == b"start":
            result_label = yolo_process()
            conn.sendall(str(result_label).encode())  # 결과 전송
        
        elif data == b"end":
            print("서버를 종료합니다.")
            conn.sendall(b"server is terminated")
            conn.close()
            break
        
        else:
            print("잘못된 명령입니다.")
        
        conn.close()
