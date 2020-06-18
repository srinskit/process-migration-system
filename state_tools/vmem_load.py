import re
import sys
import os
from loguru import logger


def vmem_load(dst_pid, abs_src_dir):
    logger.info(f"Restoring virtual memory")
    src_maps_file = open(f"{abs_src_dir}/proc.maps", 'r')
    src_mem_file = open(f"{abs_src_dir}/proc.mem", 'rb')

    dst_maps_file = open(f"/proc/{dst_pid}/maps", 'r')
    dst_mem_file = open(f"/proc/{dst_pid}/mem", 'wb')

    logger.debug(f"Comparing mappings from /proc/{dst_pid}/maps and proc.maps")
    for l1, l2 in zip(src_maps_file.readlines(), dst_maps_file.readlines()):
        m1 = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+)', l1)
        m2 = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+)', l2)
        assert m1.group() == m2.group(), "src/dst mapping differ"
    logger.debug("Virtual memory mapping match")

    logger.debug(f"Loading virtual memory from proc.mem to /proc/{dst_pid}/mem")
    src_maps_file.seek(0)
    for line in src_maps_file.readlines():
        if line.find("vsyscall") != -1 or line.find("vdso") != -1 or line.find("vvar") != -1:
           continue
        m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+)', line)
        start = int(m.group(1), 16)
        end = int(m.group(2), 16)
        size = end - start
        chunk = src_mem_file.read(size)
        dst_mem_file.seek(start)
        bytes_written = dst_mem_file.write(chunk)
        assert bytes_written == size, "could not write chunk"
    logger.debug("Restored virtual memory state")

    src_maps_file.close()
    src_mem_file.close()
    dst_mem_file.close()
    dst_maps_file.close()


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 3:
        print("dst_pid src_dir")
        exit(1)

    src_dir = argv[2]
    if not os.path.isabs(src_dir):
        src_dir = os.path.join(os.getcwd(), src_dir)

    vmem_load(argv[1], src_dir)
