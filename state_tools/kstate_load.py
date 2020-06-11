import sys
import os


def kstate_load(dst_pid, abs_src_dir):
    fd = os.open("/dev/kstate-api", os.O_RDWR)

    req = "PUT kstate {}".format(dst_pid).encode()
    os.write(fd, req)

    src_kconf_file = open("{}/proc.kconf".format(abs_src_dir), 'r')
    kstate_size = int(src_kconf_file.readline())
    src_kconf_file.close()

    src_kstate_file = open("{}/proc.kstate".format(abs_src_dir), 'rb')
    kstate = src_kstate_file.read(kstate_size)
    src_kstate_file.close()

    os.write(fd, kstate)
    os.close(fd)


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 3:
        print("dst_pid src_dir")
        exit(1)

    src_dir = argv[2]
    if not os.path.isabs(src_dir):
        src_dir = os.path.join(os.getcwd(), src_dir)

    kstate_load(argv[1], src_dir)
