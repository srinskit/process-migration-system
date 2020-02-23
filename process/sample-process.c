#include <stdio.h>
#include <unistd.h>

int main() {
    for (int i = 1; i <= 40; ++i) {
        usleep(100000);
    }
}
