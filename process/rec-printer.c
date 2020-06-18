#include <stdio.h>
#include <unistd.h>

FILE *fp;

void rec(int i)
{
	if (i > 10)
	{
		return;
	}
	sleep(1);
	fprintf(fp, "%d\n", i);
	fflush(fp);
	rec(i + 1);
}

int main()
{
	fp = fopen("op.txt", "w");
	rec(1);
	fclose(fp);
}
