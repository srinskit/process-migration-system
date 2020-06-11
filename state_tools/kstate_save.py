import sys
import os


def kstate_save(src_pid, abs_dst_dir):
    fd = os.open("/dev/kstate-api", os.O_RDWR)

    req = "GET kstate {}".format(src_pid).encode()
    os.write(fd, req)

    res = os.read(fd, 80)
    kstate_size = int(res.decode().rstrip('\x00'))

    dst_kconf_file = open("{}/proc.kconf".format(abs_dst_dir), 'w')
    dst_kconf_file.write("{}\n".format(kstate_size))
    dst_kconf_file.close()

    kstate = os.read(fd, kstate_size)

    dst_kstate_file = open("{}/proc.kstate".format(abs_dst_dir), 'wb')
    dst_kstate_file.write(kstate)
    dst_kstate_file.close()

    os.close(fd)


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
