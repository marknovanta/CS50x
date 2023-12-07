# TODO

txt = input("Text: ")

letters = list()
for l in txt:
    if l.isalpha():
        letters.append(l)
letters_count = len(letters)

words = txt.split()
words_count = len(words)

sentences_count = 0
for l in txt:
    if l == "." or l == "?" or l == "!":
        sentences_count += 1

l = letters_count / words_count * 100
s = sentences_count / words_count * 100

index = round(0.0588 * l - 0.296 * s - 15.8)

if index >= 16:
    print("Grade 16+")
elif index < 1:
    print("Before Grade 1")
else:
    print(f"Grade {index}")
