import socket
import sys
import tqdm
import os
from shutil import make_archive
from state_tools import vmem_save, kstate_save


def send_process_state(src_pid, dst_ip):
    CHUNK_SIZE = 2048

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((dst_ip, 8220))

    abs_dst_dir = os.path.join(os.getcwd(), src_pid)
    if not os.path.exists(abs_dst_dir):
        os.makedirs(abs_dst_dir)

    vmem_save(src_pid, abs_dst_dir)
    kstate_save(src_pid, abs_dst_dir)

    make_archive(abs_dst_dir, "zip", abs_dst_dir)

    src_zip_file = "{}.zip".format(abs_dst_dir)
    src_zip_filesize = os.path.getsize(src_zip_file)

    client_socket.send(f"{src_zip_filesize}".encode())
    progress = tqdm.tqdm(range(src_zip_filesize), f"Sending process state to the destination machine",
                         unit="B", unit_scale=True, unit_divisor=1024)
    with open(src_zip_file, "rb") as f:
        for _ in range(src_zip_filesize):
            # read the bytes from the file
            bytes_read = f.read(CHUNK_SIZE)
            if not bytes_read:
                # file transmitting is done
                client_socket.shutdown(socket.SHUT_WR)
                break
            # we use sendall to assure transimission in 
            # busy networks
            client_socket.sendall(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))

    client_socket.recv(2048)
    client_socket.close()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Syntax: {} src_pid dst_ip".format(sys.argv[0]))
        exit(1)
    send_process_state(sys.argv[1], sys.argv[2])
