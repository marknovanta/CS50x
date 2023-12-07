# TODO


def main():
    n = input("CARD NUMBER: ")
    if valid_check(n):
        brand = brand_check(n)
        print(brand)
    else:
        print("INVALID")


def valid_check(number):
    numbers = list()
    for c in number:
        numbers.append(int(c))
    numbers.reverse()
    list1 = numbers[1::2]
    list2 = numbers[0::2]
    mult = list()
    for n in list1:
        mult.append(str(n * 2))
    temp = ""
    for i in mult:
        temp += i
    mult = []
    for i in temp:
        mult.append(int(i))
    mult_sum = sum(mult)
    tot = str(mult_sum + sum(list2))
    if tot[-1] == "0":
        return True
    else:
        return False


def brand_check(number):
    amex = [34, 37]
    mastercard = [51, 52, 53, 54, 55]
    visa = [4]
    if (int(number[0]) in visa) and (len(number) == 13 or len(number) == 16):
        return "VISA"
    elif (int(number[0:2]) in mastercard) and (len(number) == 16):
        return "MASTERCARD"
    elif (int(number[0:2]) in amex) and (len(number) == 15):
        return "AMEX"
    else:
        return "INVALID"


main()
