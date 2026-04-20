import re
import os
from utils import get_project_path, save_result_to_file

class ProductProcessor:
    def __init__(self):
        self.rules = []
        self.load_rules()
    
    def load_rules(self, rules_file='rules.txt'):
        rules = []
        try:
            rules_path = os.path.join(get_project_path(), rules_file)
            with open(rules_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        rules.append(line)
            rules.sort(key=len, reverse=True)
        except FileNotFoundError:
            pass
        except Exception:
            pass
        self.rules = rules
    
    def process_data(self, data):
        logs = []
        lines = data.splitlines()
        products = []
        
        for idx, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            parts = re.split(r'\s+', line)
            if len(parts) < 3:
                logs.append(f"Предупреждение: строка {idx} пропущена (некорректный формат): {line}")
                continue
            name_parts = parts[:-2]
            name = ' '.join(name_parts)
            price = parts[-2]
            try:
                quantity = int(parts[-1])
            except ValueError:
                logs.append(f"Предупреждение: строка {idx} пропущена (количество не число): {line}")
                continue
            products.append([name, price, quantity])
        
        if not products:
            logs.append("Нет корректных данных для обработки.")
            return "", logs
        
        result = {}
        for name, price, quantity in products:
            group_key = None
            name_lower = name.lower()
            for rule in self.rules:
                if rule.lower() in name_lower:
                    group_key = rule
                    break
            if group_key is None:
                group_key = name.split()[0] if name else "Без названия"
            result[group_key] = result.get(group_key, 0) + quantity
        
        result_lines = ["Результат группировки:"]
        for product, total in result.items():
            result_lines.append(f"{product}: {total}")
        result_text = "\n".join(result_lines)
        
        try:
            output_path = save_result_to_file(result_text)
            logs.append(f"Результат сохранён в файл: {output_path}")
        except Exception as e:
            logs.append(str(e))
        
        logs.append("Операция завершена.")
        return result_text, logs