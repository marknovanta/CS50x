#include <cs50.h>
#include <stdio.h>

int get_cents(void);
int calculate_quarters(int cents);
int calculate_dimes(int cents);
int calculate_nickels(int cents);
int calculate_pennies(int cents);

int main(void)
{
    // Ask how many cents the customer is owed
    int cents = get_cents();

    // Calculate the number of quarters to give the customer
    int quarters = calculate_quarters(cents);
    cents = cents - quarters * 25;

    // Calculate the number of dimes to give the customer
    int dimes = calculate_dimes(cents);
    cents = cents - dimes * 10;

    // Calculate the number of nickels to give the customer
    int nickels = calculate_nickels(cents);
    cents = cents - nickels * 5;

    // Calculate the number of pennies to give the customer
    int pennies = calculate_pennies(cents);
    cents = cents - pennies * 1;

    // Sum coins
    int coins = quarters + dimes + nickels + pennies;

    // Print total number of coins to give the customer
    printf("%i\n", coins);
}

int get_cents(void)
{
    // TODO
    int amount;
    do
    {
        amount = get_int("Number of cents: ");
    }
    while (amount < 0);
    return amount;
}

int calculate_quarters(int cents)
{
    // TODO
    if (cents >= 25 && cents <= 49)
    {
        return 1;
    }
    else if (cents >= 50 && cents <= 74)
    {
        return 2;
    }
    else if (cents >= 75 && cents <= 99)
    {
        return 3;
    }
    else if (cents >= 100 && cents <= 124)
    {
        return 4;
    }
    else if (cents >= 125 && cents <= 149)
    {
        return 5;
    }
    else if (cents >= 150 && cents <= 174)
    {
        return 6;
    }
    else
    {
        return 0;
    }
}

int calculate_dimes(int cents)
{
    // TODO
    if (cents >= 10 && cents <= 19)
    {
        return 1;
    }
    else if (cents >= 20 && cents <= 29)
    {
        return 2;
    }
    else if (cents >= 30 && cents <= 39)
    {
        return 3;
    }
    else if (cents >= 40 && cents <= 49)
    {
        return 4;
    }
    else if (cents >= 50 && cents <= 59)
    {
        return 5;
    }
    else if (cents >= 60 && cents <= 69)
    {
        return 6;
    }
    else if (cents >= 70 && cents <= 79)
    {
        return 7;
    }
    else if (cents >= 80 && cents <= 89)
    {
        return 8;
    }
    else if (cents >= 90 && cents <= 99)
    {
        return 9;
    }
    else
    {
        return 0;
    }
}

int calculate_nickels(int cents)
{
    // TODO
    if (cents >= 5 && cents <= 9)
    {
        return 1;
    }
    else if (cents >= 10 && cents <= 14)
    {
        return 2;
    }
    else if (cents >= 15 && cents <= 20)
    {
        return 3;
    }
    else if (cents >= 21 && cents <= 24)
    {
        return 4;
    }
    else if (cents >= 25 && cents <= 29)
    {
        return 5;
    }
    else
    {
        return 0;
    }
}

int calculate_pennies(int cents)
{
    // TODO
    if (cents > 0)
    {
        return cents;
    }
    else
    {
        return 0;
    }
}
