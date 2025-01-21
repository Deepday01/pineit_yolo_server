import socket
import tkinter as tk


# 서버 정보 설정
HOST = "127.0.0.1"  
PORT = 5959         


# 서버와 통신하는 함수
def send_message(message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(message.encode())
    except Exception as e:
        print(f"에러 발생: {e}")
        
        
def create_gui():
    root = tk.Tk()
    root.title("신호전송")
    root.geometry("300x200")

    label = tk.Label(root, text="서버에 신호전송:", font=("Arial,12")) # 텍스트 화면에 출력
    label.pack(pady=10) # label을 창에 추가하며 위젝의 위아래 여백을 10픽셀로 설정

    start_button = tk.Button(root, text="Send START", command=lambda: send_message("start"),bg="green",fg="white")
    start_button.pack(pady=10, ipadx=20, ipady=10)

    end_button = tk.Button(root, text="Send End", command=lambda: send_message("end"), bg="red", fg="white")
    end_button.pack(pady=10, ipadx=20, ipady=10)

    root.mainloop()  # GUI 실행 
    
    
# 프로그램 실행
if __name__ == "__main__":
    print("client시작, 서버에 메시지 전송")
    send_message("start")  # 프로그램 시작 시 "start" 메시지 전송
    create_gui()    # GUI 실행, end 전송
