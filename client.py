import socket
import time
import sys
import re

CHUNK_SIZE = 2048

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((sys.argv[3], 8220))

src_pid = sys.argv[1]
src_maps_file = open("/proc/{}/maps".format(src_pid), 'r')
src_mem_file = open("/proc/{}/mem".format(src_pid), 'rb')

client_socket.send(sys.argv[2].encode())

for line in src_maps_file.readlines():
    m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
    # if line.find("vsyscall") != -1 or line.find("vdso") != -1 or line.find("vvar") != -1:
    #     continue
    if line.find("stack") == -1 and line.find("heap") == -1:
        continue
    if m.group(3) == 'r':
        start = int(m.group(1), 16)
        end = int(m.group(2), 16)
        print(m.group(1), m.group(2))
        for start_i in range(start, end, CHUNK_SIZE):
            src_mem_file.seek(start_i)
            chunk = src_mem_file.read(CHUNK_SIZE)
            client_socket.send(str(start_i).encode())
            client_socket.recv(2048)
            client_socket.send(chunk)
            client_socket.recv(2048)
            print("Sent:", start_i, "->", len(chunk))

client_socket.send("done".encode())
client_socket.recv(2048)
client_socket.close()
