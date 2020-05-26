#include <stdio.h>
#include <unistd.h>

int main()
{
	FILE *fp = fopen("op", "w");
	for (int i = 1; i <= 40; ++i)
	{
		fprintf(fp, "%d\n", i);
		fflush(fp);
		usleep(100000);
	}
	fclose(fp);
}
