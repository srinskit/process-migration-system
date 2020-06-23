import socket
import sys
import tqdm
import os
from shutil import make_archive, rmtree
from state_tools import vmem_save, kstate_save
from loguru import logger

logger.remove()
logger.add(sys.stdout, colorize=True,
           format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<cyan>{function: <16}</cyan> | "
           "<level>{message}</level>"
           )


def migrate(src_pid, dst_ip):
    print()
    logger.info(f"Initiating live-migration of process {src_pid} to {dst_ip}")

    abs_dst_dir = os.path.join(os.getcwd(), src_pid)
    if not os.path.exists(abs_dst_dir):
        os.makedirs(abs_dst_dir)

    vmem_save(src_pid, abs_dst_dir)
    kstate_save(src_pid, abs_dst_dir)

    logger.info("Compressing state data")
    make_archive(abs_dst_dir, "zip", abs_dst_dir)
    rmtree(abs_dst_dir)

    src_zip_file = "{}.zip".format(abs_dst_dir)
    src_zip_filesize = os.path.getsize(src_zip_file)

    logger.info(f"Sending data to {dst_ip}")
    CHUNK_SIZE = 2048
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((dst_ip, 8220))

    logger.info("Sending metadata")
    logger.debug(f"Size of state data: {src_zip_filesize} bytes")
    client_socket.send(f"{src_zip_filesize}".encode())

    logger.info("Sending state data")
    print()
    progress = tqdm.tqdm(range(src_zip_filesize),
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

    progress.close()
    print()

    logger.info(f"Waiting for {dst_ip} to restore state")
    client_socket.recv(2048)
    client_socket.close()

    logger.info("Live-migration complete")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Syntax: {} src_pid dst_ip".format(sys.argv[0]))
        exit(1)
    migrate(sys.argv[1], sys.argv[2])
