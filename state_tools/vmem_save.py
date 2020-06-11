import re
import sys
import os


def vmem_save(src_pid, abs_dst_dir):
    src_maps_file = open("/proc/{}/maps".format(src_pid), 'r')
    src_mem_file = open("/proc/{}/mem".format(src_pid), 'rb')

    dst_maps_file = open("{}/proc.maps".format(abs_dst_dir), 'w')
    dst_mem_file = open("{}/proc.cmem".format(abs_dst_dir), 'wb')

    for line in src_maps_file.readlines():
        dst_maps_file.write(line)
        if line.find("vsyscall") != -1 or line.find("vdso") != -1 or line.find("vvar") != -1:
            continue
        m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+)', line)
        start = int(m.group(1), 16)
        end = int(m.group(2), 16)
        size = end - start
        src_mem_file.seek(start)
        chunk = src_mem_file.read(size)
        bytes_written = dst_mem_file.write(chunk)
        assert bytes_written == size

    src_maps_file.close()
    src_mem_file.close()
    dst_maps_file.close()
    dst_mem_file.close()


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

    vmem_save(argv[1], dst_dir)
