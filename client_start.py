import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 5959  # The port used by the server

#Terminate = True

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    #if Terminate :
        #s.sendall(b"_END_")   # to terminate server
    #else :  
    s.sendall(b"start")
    data = s.recv(1024)
    print(f"Received {data!r}")