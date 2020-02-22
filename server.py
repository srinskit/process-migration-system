import socket
import sys

host = 'localhost'
port = 8220
address = (host, port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(address)
server_socket.listen(5)

flag = 1 #for server to identify start or chunk. 1 = Start ; 0 = Chunk.

print("Listening for client . . .")
conn, address = server_socket.accept()
print("Connected to client at ", address)
while True:
    output = conn.recv(2048)
    if output == "disconnect".encode():
        conn.close()
        sys.exit("Received disconnect message.  Shutting down.")
        conn.send("dack".encode())
    elif output:
        print("Message received from client:")
        if flag == 1:
            print("Start : " + output.decode())
            flag = 0
        else:
            print("Chunk : " + output.decode())
            flag = 1
        conn.send("ack".encode())
