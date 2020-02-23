#include <stdio.h>
#include <unistd.h>

int child(int arg) {
    char file_name[20];
    sprintf(file_name, "child-%d.txt", arg);
    FILE *fp = fopen(file_name, "w");
    for (int i = 1; i <= 40; ++i) {
        usleep(100000);
        fprintf(fp, "%d\n", i);
        fflush(fp);
    }
    fclose(fp);
}

int main() {
    int n = 2;
    for (int i = 0; i < n; ++i) {
        if (fork() == 0) {
            return child(i);
        }
    }
}
