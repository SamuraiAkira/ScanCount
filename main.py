import os

input_file = "input.txt"
output_file = "output.txt"

try:
    with open(input_file, "r", encoding="utf-8") as source:
        content = source.read()
except FileNotFoundError:
    print(f"Ошибка: файл '{input_file}' не найден.")
    exit(1)

with open(output_file, "w", encoding="utf-8") as copy:
    copy.write(content)

print(content)

with open(input_file, "w", encoding="utf-8") as f:
    f.truncate(0)
print("\nФайл очищен")

print("\nОперация окончена")