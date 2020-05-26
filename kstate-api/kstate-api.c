#define MODULE
#define LINUX
#define __KERNEL__

#include <linux/fs.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/pid.h>
#include <linux/pid_namespace.h>
#include <linux/sched/task_stack.h>
#include <linux/uaccess.h>

#define SUCCESS 0
#define DEVICE_NAME "kstate-api"
#define BUFF_SIZE 1024

// Device states
#define ENTRY 0
#define RECEIVED_GET_KSTATE 1
#define SENT_KSTATE_SIZE 2
#define RECEIVED_PUT_KSTATE 3

struct KState
{
	char pt_regs[sizeof(struct pt_regs)];
};

int init_module(void);
void cleanup_module(void);
static int device_open(struct inode *, struct file *);
static int device_release(struct inode *, struct file *);
static ssize_t device_read(struct file *, char *, size_t, loff_t *);
static ssize_t device_write(struct file *, const char *, size_t, loff_t *);

static int Major;
static int Device_Open = 0;
static int device_state;
static struct KState kstate;
static int pid;

static struct file_operations fops = {.read = device_read,
									  .write = device_write,
									  .open = device_open,
									  .release = device_release};

int init_module(void)
{
	Major = register_chrdev(0, DEVICE_NAME, &fops);

	if (Major < 0)
	{
		printk("Registering the character device failed with %d\n", Major);
		return Major;
	}
	printk(KERN_INFO "kstate-api spawned. Major: %d", Major);
	return SUCCESS;
}

void cleanup_module(void)
{
	unregister_chrdev(Major, DEVICE_NAME);
	printk(KERN_INFO "kstate-api killed");
}

/* Methods */

/* Called when a process tries to open the device file, like
 * "cat /dev/mycharfile"
 */
static int device_open(struct inode *inode, struct file *file)
{
	if (Device_Open)
		return -EBUSY;
	Device_Open++;
	device_state = ENTRY;
	return SUCCESS;
}

/* Called when a process closes the device file */
static int device_release(struct inode *inode, struct file *file)
{
	Device_Open--;
	device_state = ENTRY;
	return SUCCESS;
}

/* Called when a process, which already opened the dev file, attempts to
   read from it.
*/
static ssize_t device_read(struct file *filp,
						   char *buffer,   /* The buffer to fill with data */
						   size_t length,  /* The length of the buffer     */
						   loff_t *offset) /* Our offset in the file       */
{
	if (device_state == RECEIVED_GET_KSTATE)
	{
		char buff[BUFF_SIZE];
		int op_len = 0;
		sprintf(buff, "%lu\n", sizeof(kstate));
		op_len = strnlen(buff, sizeof(buff));
		if (op_len < sizeof(buff) && op_len + 1 <= length)
		{
			copy_to_user(buffer, buff, op_len + 1);
			printk(KERN_INFO "%s: Sent kstate size\n", DEVICE_NAME);
			device_state = SENT_KSTATE_SIZE;
			return op_len + 1;
		}
	}
	else if (device_state == SENT_KSTATE_SIZE)
	{
		if (sizeof(kstate) <= length)
		{
			copy_to_user(buffer, &kstate, sizeof(kstate));
			printk(KERN_INFO "%s: Sent kstate\n", DEVICE_NAME);
			device_state = ENTRY;
			return sizeof(kstate);
		}
	}
	printk(KERN_INFO "%s: Protocol error\n", DEVICE_NAME);
	return -EINVAL;
}

/*  Called when a process writes to dev file: echo "hi" > /dev/hello */
static ssize_t device_write(struct file *filp,
							const char *buffer, /* The buffer to fill with data */
							size_t length,		/* The length of the buffer     */
							loff_t *offset)		/* Our offset in the file       */
{
	if (device_state == ENTRY)
	{
		char buff[BUFF_SIZE];

		if (length >= BUFF_SIZE)
			return -EINVAL;
		copy_from_user(buff, buffer, length);
		buff[length] = 0;

		if (sscanf(buff, "GET kstate %d", &pid) == 1)
		{
			struct task_struct *tsk;
			rcu_read_lock();
			tsk = pid_task(find_pid_ns(pid, &init_pid_ns), PIDTYPE_PID);
			memcpy(kstate.pt_regs, task_pt_regs(tsk), sizeof(struct pt_regs));
			rcu_read_unlock();

			printk(KERN_INFO "%s: Saved kstate of %d\n", DEVICE_NAME, pid);
			device_state = RECEIVED_GET_KSTATE;
			return length;
		}
		else if (sscanf(buff, "PUT kstate %d", &pid) == 1)
		{
			printk(KERN_INFO "%s: Ready to recv kstate of %d\n", DEVICE_NAME, pid);
			device_state = RECEIVED_PUT_KSTATE;
			return length;
		}
	}
	else if (device_state == RECEIVED_PUT_KSTATE)
	{
		struct task_struct *tsk;

		if (length != sizeof(kstate))
			return -EINVAL;
		copy_from_user(&kstate, buffer, length);

		rcu_read_lock();
		tsk = pid_task(find_pid_ns(pid, &init_pid_ns), PIDTYPE_PID);
		memcpy(task_pt_regs(tsk), kstate.pt_regs, sizeof(struct pt_regs));
		rcu_read_unlock();

		printk(KERN_INFO "%s: Loaded kstate of %d\n", DEVICE_NAME, pid);
		device_state = ENTRY;
		return length;
	}
	printk(KERN_INFO "%s: Protocol error\n", DEVICE_NAME);
	return -EINVAL;
}

MODULE_LICENSE("GPL");