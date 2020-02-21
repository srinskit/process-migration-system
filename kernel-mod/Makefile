mod_name = regcp
obj-m += $(mod_name).o

all:
	sudo rmmod $(mod_name) || echo
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) modules
	sudo insmod $(mod_name).ko
	sudo mknod /dev/$(mod_name) c 238 0 -m 777 || echo
clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) clean
