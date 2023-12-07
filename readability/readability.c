#include <cs50.h>
#include <ctype.h>
#include <math.h>
#include <stdio.h>
#include <string.h>

int get_grade(string txt);
int get_letters(string txt);
int get_words(string txt);
int get_sentences(string txt);

int main(void)
{
    string text = get_string("Text: ");
    int grade = get_grade(text);
    if (grade < 1)
    {
        printf("Before Grade 1\n");
    }
    else if (grade > 16)
    {
        printf("Grade 16+\n");
    }
    else
    {
        printf("Grade %i\n", grade);
    }
}

int get_grade(string txt)
{
    int letters = get_letters(txt);
    int words = get_words(txt);
    int sentences = get_sentences(txt);

    float L = (float) letters / words * 100;
    float S = (float) sentences / words * 100;

    float index = round(0.0588 * L - 0.296 * S - 15.8);
    return index;
}

int get_letters(string txt)
{
    int letters = 0;
    for (int i = 0, size = strlen(txt); i < size; i++)
    {
        if (isupper(txt[i]) || islower(txt[i]))
        {
            letters++;
        }
    }
    return letters;
}

int get_words(string txt)
{
    int spaces = 0;
    for (int i = 0, size = strlen(txt); i < size; i++)
    {
        if (isspace(txt[i]))
        {
            spaces++;
        }
    }
    int words = spaces + 1;
    return words;
}

int get_sentences(string txt)
{
    int sentences = 0;
    for (int i = 0, size = strlen(txt); i < size; i++)
    {
        if (txt[i] == 33 || txt[i] == 63 || txt[i] == 46)
        {
            sentences++;
        }
    }
    return sentences;
}