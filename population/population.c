#include <cs50.h>
#include <stdio.h>

int main(void)
{
    int start;
    do
    {
        start = get_int("How many llamas at the beginning? ");
    }
    while (start < 9);

    int end;
    do
    {
        end = get_int("How many llamas in the end? ");
    }
    while (end < start);

    int years = 0;
    while (start < end)
    {
        int born = start / 3;
        int dead = start / 4;
        start += born - dead;
        years++;
    }
    printf("Years: %i\n", years);
}