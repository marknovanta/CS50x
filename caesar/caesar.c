#include <cs50.h>
#include <ctype.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

string encript(string txt, int k);

int main(int argc, string argv[])
{
    int key;
    if (argc == 2)
    {
        for (int i = 0, l = strlen(argv[1]); i < l; i++)
        {
            if (isalpha(argv[1][i]) || ispunct(argv[1][i]))
            {
                printf("Enter digits as arg\n");
                return 1;
            }
            else
            {
                // Get the key and convert it into an integer
                key = atoi(argv[1]);
            }
        }
    }
    else
    {
        printf("Enter just one command-line arg\n");
        return 1;
    }

    string text = get_string("plaintext: ");

    string encripted = encript(text, key);
    printf("ciphertext: %s\n", encripted);
}

string encript(string txt, int k)
{
    for (int i = 0, l = strlen(txt); i < l; i++)
    {
        if (isalpha(txt[i]))
        {
            int move_left = k;
            if (isupper(txt[i]))
            {
                // 65-90
                if ((txt[i] + k) < 90)
                {
                    txt[i] += k;
                }
                else
                {
                    while (move_left > 0)
                    {
                        if (txt[i] + 1 > 90)
                        {
                            txt[i] = 65;
                        }
                        else
                        {
                            txt[i]++;
                        }
                        move_left--;
                    }
                }
            }
            else
            {
                // 97-122
                if ((txt[i] + k) < 122)
                {
                    txt[i] += k;
                }
                else
                {
                    while (move_left > 0)
                    {
                        if (txt[i] + 1 > 122)
                        {
                            txt[i] = 97;
                        }
                        else
                        {
                            txt[i]++;
                        }
                        move_left--;
                    }
                }
            }
        }
    }
    return txt;
}
