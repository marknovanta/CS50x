# TODO
while True:
    try:
        h = int(input("H: "))
        if h >= 1 and h <= 8:
            break
    except:
        print("Not valid number")
spaces = h - 1
count = 1
for i in range(h):
    print((" " * spaces) + ("#" * count) + (" " * 2) + ("#" * count))
    spaces -= 1
    count += 1
