import sys
import os
from loguru import logger


def kstate_save(src_pid, abs_dst_dir):
    logger.info(f"Saving kernel state")

    fd = os.open("/dev/kstate-api", os.O_RDWR)

    req = f"GET kstate {src_pid}"
    logger.debug(f"Sending query '{req}' to /dev/kstate-api")
    os.write(fd, req.encode())

    logger.debug("Receiving metadata from /dev/kstate-api")
    res = os.read(fd, 80)
    kstate_size = int(res.decode().rstrip('\x00'))
    logger.debug(f"Received kernel state size: {kstate_size} bytes")

    logger.debug("Saving metadata to proc.kconf")
    dst_kconf_file = open("{}/proc.kconf".format(abs_dst_dir), 'w')
    dst_kconf_file.write("{}\n".format(kstate_size))
    dst_kconf_file.close()

    logger.debug("Receiving kernel state data from /dev/kstate-api")
    kstate = os.read(fd, kstate_size)

    logger.debug("Saving kernel state data to proc.kstate")
    dst_kstate_file = open("{}/proc.kstate".format(abs_dst_dir), 'wb')
    dst_kstate_file.write(kstate)
    dst_kstate_file.close()

    os.close(fd)
    logger.debug(f"Saved kernel state")



if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 3:
        print("src_pid dst_dir")
        exit(1)

    dst_dir = argv[2]
    if not os.path.isabs(dst_dir):
        dst_dir = os.path.join(os.getcwd(), dst_dir)
    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    kstate_save(argv[1], dst_dir)
