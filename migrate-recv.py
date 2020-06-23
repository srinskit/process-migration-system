import socket
import sys
import subprocess
import threading
import signal
import tqdm
import os
from shutil import unpack_archive, rmtree
from state_tools import kstate_load, vmem_load
from loguru import logger

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<cyan>{function: <16}</cyan> | "
           "<level>{message}</level>"
           )

CHUNK_SIZE = 2048
BASE_PATH = "/home/ubuntu/mp-executables/"

host = '0.0.0.0'
port = 8220
address = (host, port)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(address)
server_socket.listen(3)


def handle_request(client_socket, addr):
    print()
    dst_pid = sys.argv[1]

    logger.info(f"Recevied live-migration request from {addr[0]}")
    logger.info(f"Target process {dst_pid}")

    logger.info("Receiving data")
    logger.info("Receiving metadata")
    dst_proc_name = dst_pid
    dst_zip_filesize = int(client_socket.recv(2048).decode())
    logger.debug(f"Size of state data: {dst_zip_filesize} bytes")

    dst_zip_file = os.path.join(os.getcwd(), f"{dst_proc_name}.zip")
    dst_dir = os.path.join(os.getcwd(), dst_proc_name)

    # p = subprocess.Popen([BASE_PATH + received_message.decode()])
    # p.send_signal(signal.SIGSTOP)
    # print("PID:", p.pid)

    logger.info("Receiving state data")
    print()
    progress = tqdm.tqdm(range(dst_zip_filesize), unit="B",
                         unit_scale=True, unit_divisor=1024)
    with open(dst_zip_file, "wb") as f:
        for _ in range(dst_zip_filesize):
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

    progress.close()
    print()

    logger.info("Decompressing state data")
    unpack_archive(dst_zip_file, dst_dir, "zip")

    vmem_load(dst_pid, dst_dir)
    kstate_load(dst_pid, dst_dir)

    rmtree(dst_dir)
    client_socket.send("ack".encode())
    client_socket.close()
    logger.info("Live-migration complete")


logger.info(f"Server started")
try:
    while True:
        c, addr = server_socket.accept()
        # x = threading.Thread(target=handle_request, args=(c, addr))
        # x.start()
        handle_request(c, addr)
except KeyboardInterrupt:
    print()
finally:
    logger.info(f"Server stopped")

server_socket.close()
