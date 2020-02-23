import socket
import sys
import subprocess
import threading
import signal


CHUNK_SIZE = 2048
BASE_PATH = "/home/ubuntu/mp-executables/"

host = '0.0.0.0'
port = 8220
address = (host, port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(address)
server_socket.listen(3)


def on_new_client(client_socket, addr):
    flag = 1
    received_message = client_socket.recv(CHUNK_SIZE)

    # p = subprocess.Popen([BASE_PATH + received_message.decode()])
    # p.send_signal(signal.SIGSTOP)
    # print("PID:", p.pid)

    dst_pid = sys.argv[1]
    dst_maps_file = open("/proc/{}/maps".format(dst_pid), 'r')
    dst_mem_file = open("/proc/{}/mem".format(dst_pid), 'wb')
    print(dst_maps_file.read())
    start = ""
    chunk = ""
    while True:
        received_message = client_socket.recv(CHUNK_SIZE)
        if received_message != b'done':
            # print("Message received from client:")
            if flag == 1:
                # print("Start : " + received_message.decode())
                try:
                    start = int(received_message.decode())
                    flag = 0
                except:
                    print("Except:", received_message)
                    dst_mem_file.close()
            else:
                # print("Chunk : " + received_message.decode())
                chunk = received_message
                dst_mem_file.seek(start)
                bytes_written = dst_mem_file.write(chunk)
                print(hex(start), bytes_written)
                flag = 1
            client_socket.send("ack".encode())
        else:
            print("Done received")
            client_socket.send("ack".encode())
            dst_mem_file.close()


while True:
    c, addr = server_socket.accept()
    x = threading.Thread(target=on_new_client, args=(c, addr))
    x.start()

s.close()
