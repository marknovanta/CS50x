#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <string.h>

// Points assigned to each letter of the alphabet
int POINTS[] = {1, 3, 3, 2, 1, 4, 2, 4, 1, 8, 5, 1, 3, 1, 1, 3, 10, 1, 1, 1, 1, 4, 4, 8, 4, 10};

int compute_score(string word);

int main(void)
{
    // Get input words from both players
    string word1 = get_string("Player 1: ");
    string word2 = get_string("Player 2: ");

    // Score both words
    int score1 = compute_score(word1);
    int score2 = compute_score(word2);

    // TODO: Print the winner
    if (score1 > score2)
    {
        printf("Player 1 wins!\n");
    }
    else if (score1 < score2)
    {
        printf("Player 2 wins!\n");
    }
    else
    {
        printf("Tie!\n");
    }
}

int compute_score(string word)
{
    // TODO: Compute and return score for string
    int value = 0;
    for (int i = 0, lenght = strlen(word); i < lenght; i++)
    {
        word[i] = tolower(word[i]);
        switch (word[i])
        {
            case 'a':
                value += POINTS[0];
                break;
            case 'b':
                value += POINTS[1];
                break;
            case 'c':
                value += POINTS[2];
                break;
            case 'd':
                value += POINTS[3];
                break;
            case 'e':
                value += POINTS[4];
                break;
            case 'f':
                value += POINTS[5];
                break;
            case 'g':
                value += POINTS[6];
                break;
            case 'h':
                value += POINTS[7];
                break;
            case 'i':
                value += POINTS[8];
                break;
            case 'j':
                value += POINTS[9];
                break;
            case 'k':
                value += POINTS[10];
                break;
            case 'l':
                value += POINTS[11];
                break;
            case 'm':
                value += POINTS[12];
                break;
            case 'n':
                value += POINTS[13];
                break;
            case 'o':
                value += POINTS[14];
                break;
            case 'p':
                value += POINTS[15];
                break;
            case 'q':
                value += POINTS[16];
                break;
            case 'r':
                value += POINTS[17];
                break;
            case 's':
                value += POINTS[18];
                break;
            case 't':
                value += POINTS[19];
                break;
            case 'u':
                value += POINTS[20];
                break;
            case 'v':
                value += POINTS[21];
                break;
            case 'w':
                value += POINTS[22];
                break;
            case 'x':
                value += POINTS[23];
                break;
            case 'y':
                value += POINTS[24];
                break;
            case 'z':
                value += POINTS[25];
                break;
            default:
                value += 0;
        }
    }
    return value;
}
