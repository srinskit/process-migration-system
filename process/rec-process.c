#include <stdio.h>
#include <unistd.h>

FILE *fp;

void rec(int i) {
    if (i < 100) {
        usleep(100000);
        fprintf(fp, "%d\n", i);
        fflush(fp);
        rec(i + 1);
    }
}

int child(int arg) {
    char file_name[20];
    sprintf(file_name, "child-%d.txt", arg);
    fp = fopen(file_name, "w");
    rec(1);
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
