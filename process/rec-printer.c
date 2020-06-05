#include <stdio.h>
#include <unistd.h>

FILE *fp;

void rec(int i)
{
	if (i > 40)
	{
		return;
	}
	fprintf(fp, "%d\n", i);
	fflush(fp);
	usleep(100000);
	rec(i + 1);
}

int main()
{
	fp = fopen("op.txt", "w");
	rec(1);
	fclose(fp);
}
