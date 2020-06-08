import socket
import sys
import subprocess
import threading
import signal
import tqdm
import os
from shutil import unpack_archive
from state_tools import kstate_load, vmem_load


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
    dst_proc_name = "sample"
    dst_zip_filesize = int(client_socket.recv(CHUNK_SIZE).decode())
    dst_zip_file = f"{dst_proc_name}.zip"

    # p = subprocess.Popen([BASE_PATH + received_message.decode()])
    # p.send_signal(signal.SIGSTOP)
    # print("PID:", p.pid)

    dst_pid = sys.argv[1]

    progress = tqdm.tqdm(range(dst_zip_filesize), f"Receiving the process state", unit="B", unit_scale=True, unit_divisor=1024)
    with open(dst_zip_file, "wb") as f:
        for _ in progress:
            # read bytes from the socket (receive)
            bytes_read = client_socket.recv(CHUNK_SIZE)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    
    client_socket.send("ack".encode())
    client_socket.close()

    dst_proc_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dst_proc")
    if not os.path.exists(dst_proc_dir):
        os.makedirs(dst_proc_dir)
    
    dst_dir = os.path.join(dst_proc_dir, dst_proc_name)
    unpack_archive(dst_zip_file, dst_dir, "zip")

    kstate_load(dst_pid, dst_dir)
    vmem_load(dst_pid, dst_dir)

    return


while True:
    c, addr = server_socket.accept()
    x = threading.Thread(target=on_new_client, args=(c, addr))
    x.start()

server_socket.close()
