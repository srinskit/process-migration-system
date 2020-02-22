import socket
import time


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_socket.connect(("localhost", 8220))

start = [ 2,4,1,3,42]
chunks = ['chunk1','chunk2','chunk3','chunk4','chunk5',]

index = 0
while True:
    data = str(start[index]) 
    print('send to server: ' + data)
    client_socket.send(data.encode())
    while client_socket.recv(2048).decode().strip() != "ack":
        print("waiting for ack")
    data = chunks[index]
    print('send to server: ' + data)
    client_socket.send(data.encode())
    print("ack received!")
    if index == 4: #condition to stop sending data from client to server.
        break
    index = index + 1

#send disconnect message                                                                                                                           
dmsg = "disconnect"
print("Disconnecting")
client_socket.send(dmsg.encode())
client_socket.close()
