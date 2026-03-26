import os, re, csv

input_file = "input.txt"
output_file = "output.txt"

try:
    with open(input_file, "r", encoding="utf-8") as source:
        products = []
        for line in source:
            line = line.strip()
            if line:
                parts = re.split(r'\s+', line)
                
                if len(parts) < 3:
                    print(f"Предупреждение: некорректная строка пропущена: {line}")
                    continue
                
                name_parts = parts[:-2]
                name = ' '.join(name_parts)
                
                price = parts[-2]
                quantity = int(parts[-1])
                
                products.append([name, price, quantity])
    
    if not products:
        print("Файл input пуст или не содержит корректных данных")
    else:
        result = {}
        for name, price, quantity in products:
            base_name = name.split()[0]
            result[base_name] = result.get(base_name, 0) + quantity

        with open(output_file, "w", encoding="utf-8", newline='') as copy:
            writer = csv.writer(copy)
            writer.writerow(["Продукт", "Общее количество"])
            for product, total in result.items():
                writer.writerow([product, total])
        
        print("Результат группировки:")
        for product, total in result.items():
            print(f"{product}, ({total})")
        
        print(f"\nЗапись сохранена в {output_file}")

except FileNotFoundError:
    print(f"Ошибка: файл '{input_file}' не найден.")
    exit(1)
except ValueError as e:
    print(f"Ошибка преобразования числа: {e}. Проверьте, что количество - это число.")
except Exception as e:
    print(f"Произошла ошибка: {e}")

try:
    with open(input_file, "w", encoding="utf-8") as f:
        f.truncate(0)
    print("\nФайл input очищен")
except Exception as e:
    print(f"Не удалось очистить файл: {e}")

print("\nОперация окончена")