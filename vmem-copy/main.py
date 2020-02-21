import re
import sys
 
 
argv = sys.argv
if len(argv) != 3:
    print(argv)
    exit(1)
 

src_pid = argv[1]
dst_pid = argv[2]

src_maps_file = open("/proc/{}/maps".format(src_pid), 'r')
src_mem_file = open("/proc/{}/mem".format(src_pid), 'rb')
dst_maps_file = open("/proc/{}/maps".format(dst_pid), 'r')
dst_mem_file = open("/proc/{}/mem".format(dst_pid), 'wb')
 
for line in src_maps_file.readlines():
    m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r])', line)
    # print(m.group(1), m.group(2), m.group(3))
    if line.find("vsyscall") != -1 or line.find("vdso") != -1 or line.find("vvar") != -1:
        continue
    if m.group(3) == 'r':
        start = int(m.group(1), 16)
        end = int(m.group(2), 16)
        # print(m.group(1), m.group(2))
        src_mem_file.seek(start)
        dst_mem_file.seek(start)
        chunk = src_mem_file.read(end - start)
        bytes_written = dst_mem_file.write(chunk)
        # print(end-start, bytes_written)
 
src_maps_file.close()
src_mem_file.close()
dst_maps_file.close()
dst_mem_file.close()
