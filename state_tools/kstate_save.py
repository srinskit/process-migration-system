import sys
import os


def kstate_save(src_pid, dst_file):
    fd = os.open("/dev/kstate-api", os.O_RDWR)

    req = "GET kstate {}".format(src_pid).encode()
    os.write(fd, req)

    res = os.read(fd, 80)
    kstate_size = int(res.decode().rstrip('\x00'))

    dst_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), dst_file)

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)
    dst_kconf_file = open("{}/proc.kconf".format(dst_dir), 'w')
    dst_kconf_file.write("{}\n".format(kstate_size))
    dst_kconf_file.close()

    kstate = os.read(fd, kstate_size)

    dst_kstate_file = open("{}/proc.kstate".format(dst_dir), 'wb')
    dst_kstate_file.write(kstate)
    dst_kstate_file.close()

    os.close(fd)


if __name__ == "__main__":
    argv = sys.argv
    if len(argv) != 3:
        print("src_pid dst_file")
        exit(1)
    kstate_save(argv[1], argv[2])
