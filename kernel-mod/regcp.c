#define MODULE
#define LINUX
#define __KERNEL__

#include <linux/fs.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/pid.h>
#include <linux/pid_namespace.h>
#include <linux/uaccess.h>

int init_module(void);
void cleanup_module(void);
static int device_open(struct inode *, struct file *);
static int device_release(struct inode *, struct file *);
static ssize_t device_read(struct file *, char *, size_t, loff_t *);
static ssize_t device_write(struct file *, const char *, size_t, loff_t *);

#define SUCCESS 0
#define DEVICE_NAME "regcp"
#define BUFF_SIZE 80

static int copy_task_struct(struct task_struct *src, struct task_struct *dst);

static int Major;           /* Major number assigned to our device driver */
static int Device_Open = 0; /* Is device open?  Used to prevent multiple
                                       access to the device */

static struct file_operations fops = {.read = device_read,
                                      .write = device_write,
                                      .open = device_open,
                                      .release = device_release};

int init_module(void) {
    Major = register_chrdev(0, DEVICE_NAME, &fops);

    if (Major < 0) {
        printk("Registering the character device failed with %d\n", Major);
        return Major;
    }
    printk(KERN_INFO "regcp spawned. Major: %d", Major);
    return 0;
}

void cleanup_module(void) {
    unregister_chrdev(Major, DEVICE_NAME);
    printk(KERN_INFO "regcp killed");
}

/* Methods */

/* Called when a process tries to open the device file, like
 * "cat /dev/mycharfile"
 */
static int device_open(struct inode *inode, struct file *file) {
    if (Device_Open) return -EBUSY;
    Device_Open++;
    return SUCCESS;
}

/* Called when a process closes the device file */
static int device_release(struct inode *inode, struct file *file) {
    Device_Open--;
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
    return -EINVAL;
}

/*  Called when a process writes to dev file: echo "hi" > /dev/hello */
static ssize_t device_write(struct file *filp,
                            const char *buff, /* The buffer to fill with data */
                            size_t length,    /* The length of the buffer     */
                            loff_t *offset)   /* Our offset in the file       */
{
    char buffer[BUFF_SIZE];
    int pid1, pid2;
    struct task_struct *tsk1, *tsk2;
    if (length >= BUFF_SIZE) return -EINVAL;

    copy_from_user(buffer, buff, BUFF_SIZE);
    buffer[length] = 0;

    sscanf(buffer, "%d %d", &pid1, &pid2);

    printk(KERN_DEBUG "%s: KSTATE %d >>> %d\n", DEVICE_NAME, pid1, pid2);
    rcu_read_lock();
    tsk1 = pid_task(find_pid_ns(pid1, &init_pid_ns), PIDTYPE_PID);
    tsk2 = pid_task(find_pid_ns(pid2, &init_pid_ns), PIDTYPE_PID);
    if (!copy_task_struct(tsk1, tsk2)) {
        printk(KERN_DEBUG "%s: KSTATE copied\n", DEVICE_NAME);
    } else {
        printk(KERN_DEBUG "%s: KSTATE copy failed\n", DEVICE_NAME);
    }
    rcu_read_unlock();
    return length;
}

static int copy_task_struct(struct task_struct *src, struct task_struct *dst) {

    return SUCCESS;
}

MODULE_LICENSE("GPL");