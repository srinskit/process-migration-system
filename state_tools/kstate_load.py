import sys
import os


def kstate_load(dst_pid, src_file):
    fd = os.open("/dev/kstate-api", os.O_RDWR)

    req = "PUT kstate {}".format(dst_pid).encode()
    os.write(fd, req)

    src_kconf_file = open("{}/proc.kconf".format(src_file), 'r')
    kstate_size = int(src_kconf_file.readline())
    src_kconf_file.close()

    src_kstate_file = open("{}/proc.kstate".format(src_file), 'rb')
    kstate = src_kstate_file.read(kstate_size)
    src_kstate_file.close()

    os.write(fd, kstate)
    os.close(fd)


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 3:
        print("dst_pid src_file")
        exit(1)
    kstate_load(argv[1], argv[2])
