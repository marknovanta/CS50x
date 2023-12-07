#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int height;
    do
    {
        height = get_int("Height: ");
    }
    while (height < 1 || height > 8);

    int gap = 2;
    int spaces = height - 1;
    int left_blocks = 1;
    int right_blocks = 1;

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < spaces; j++)
        {
            printf(" ");
        }
        spaces--;
        for (int lb = 0; lb < left_blocks; lb++)
        {
            printf("#");
        }
        left_blocks++;
        for (int g = 0; g < gap; g++)
        {
            printf(" ");
        }
        for (int rb = 0; rb < right_blocks; rb++)
        {
            printf("#");
        }
        right_blocks++;
        printf("\n");
    }
}