mod_name = kstate-api
obj-m += $(mod_name).o

all:
	sudo rmmod $(mod_name) || echo
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) modules
	sudo insmod $(mod_name).ko
ifdef major
	sudo mknod /dev/$(mod_name) c $(major) 0 -m 777 || echo
endif

clean:
	make -C /lib/modules/$(shell uname -r)/build M=$(shell pwd) clean
	sudo rm -f /dev/$(mod_name)