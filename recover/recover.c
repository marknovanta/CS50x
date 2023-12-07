#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    FILE *file = fopen(argv[1], "r");
    if (file == NULL)
        return 1;

    BYTE buffer[512];
    int counter = 0;
    char filename[8];
    FILE *imgp = NULL;

    while (fread(buffer, sizeof(BYTE) * 512, 1, file) == 1)
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0)
        {
            if (imgp != NULL)
                fclose(imgp);

            sprintf(filename, "%03i.jpg", counter);
            imgp = fopen(filename, "w");
            counter++;
        }
        if (imgp != NULL)
            fwrite(buffer, sizeof(BYTE) * 512, 1, imgp);
    }
    fclose(imgp);
    fclose(file);
}
