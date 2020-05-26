import re
import sys


def vmem_save(src_pid, dst_file):
    src_maps_file = open("/proc/{}/maps".format(src_pid), 'r')
    src_mem_file = open("/proc/{}/mem".format(src_pid), 'rb')

    dst_maps_file = open("{}.maps".format(dst_file), 'w')
    dst_mem_file = open("{}.cmem".format(dst_file), 'wb')

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
        print("src_pid dst_file")
        exit(1)
    vmem_save(argv[1], argv[2])
