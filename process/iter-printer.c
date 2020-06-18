#include <stdio.h>
#include <unistd.h>

int main()
{
	FILE *fp = fopen("op.txt", "w");
	for (int i = 1; i <= 10; ++i)
	{
		sleep(1);
		fprintf(fp, "%d\n", i);
		fflush(fp);
	}
	fclose(fp);
}
