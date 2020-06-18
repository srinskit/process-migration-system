import sys
import os
from loguru import logger


def kstate_load(dst_pid, abs_src_dir):
    logger.info(f"Restoring kernel state")

    logger.debug("Reading metadata from proc.kconf")
    src_kconf_file = open(f"{abs_src_dir}/proc.kconf", 'r')
    kstate_size = int(src_kconf_file.readline())
    src_kconf_file.close()

    logger.debug("Reading kernel state data from proc.kstate")
    src_kstate_file = open(f"{abs_src_dir}/proc.kstate", 'rb')
    kstate = src_kstate_file.read(kstate_size)
    src_kstate_file.close()

    fd = os.open("/dev/kstate-api", os.O_RDWR)

    req = f"PUT kstate {dst_pid}"
    logger.debug(f"Sending query '{req}' to /dev/kstate-api")
    os.write(fd, req.encode())

    logger.debug("Sending kernel state data to /dev/kstate-api")
    os.write(fd, kstate)
    os.close(fd)

    logger.debug("Restored kernel state")


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 3:
        print("dst_pid src_dir")
        exit(1)

    src_dir = argv[2]
    if not os.path.isabs(src_dir):
        src_dir = os.path.join(os.getcwd(), src_dir)

    kstate_load(argv[1], src_dir)
