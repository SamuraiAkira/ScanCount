import os
import sys
import re
import tkinter as tk
from tkinter import scrolledtext, messagebox

def resource_path(relative_path):
    """Получить абсолютный путь к ресурсу, работает для dev и для PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class ProductProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ScanCount")
        
        try:
            icon_path = resource_path("logo.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"Иконка не найдена: {icon_path}")
        except Exception as e:
            print(f"Не удалось установить иконку: {e}")
        
        self.root.geometry("750x650")
        self.root.configure(bg="#2a2a3a")
        self.root.resizable(True, True)
        
        self.rules = []
        self.create_widgets()
        self.load_rules()
        self.center_window()

    def load_rules(self, rules_file="rules.txt"):
        """Загружает правила группировки из файла."""
        rules = []
        try:
            rules_path = resource_path(rules_file)
            with open(rules_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        rules.append(line)
            rules.sort(key=len, reverse=True)
            if rules:
                self.log(f"Загружено {len(rules)} правил группировки из {rules_file}")
            else:
                self.log(f"Файл {rules_file} не содержит правил")
        except FileNotFoundError:
            self.log(f"Файл {rules_file} не найден. Группировка будет по первому слову.")
        except Exception as e:
            self.log(f"Ошибка при загрузке правил: {e}")
        self.rules = rules

    def center_window(self):
        """Центрирует окно на экране"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        input_frame = tk.LabelFrame(self.root, text="Входные данные", bg="#2a2a3a", fg="white",
                                    font=("Arial", 10, "bold"), padx=5, pady=5)
        input_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, height=12,
                                                    bg="#3a3a4a", fg="white", insertbackground="white")
        self.input_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.context_menu = tk.Menu(self.input_text, tearoff=0)
        self.context_menu.add_command(label="Вырезать", command=self.cut_text)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)
        self.input_text.bind("<Button-3>", self.show_context_menu)

        button_frame = tk.Frame(input_frame, bg="#2a2a3a")
        button_frame.pack(fill="x", pady=5)

        paste_btn = tk.Button(button_frame, text="Вставить из буфера", command=self.paste_text,
                              bg="#4a6fa5", fg="white", font=("Arial", 9))
        paste_btn.pack(side="left", padx=5)

        clear_input_btn = tk.Button(button_frame, text="Очистить поле", command=self.clear_input_text,
                                    bg="#4a6fa5", fg="white", font=("Arial", 9))
        clear_input_btn.pack(side="left", padx=5)

        hint_label = tk.Label(input_frame, text="Формат строк: название цена количество (через пробел)",
                              bg="#2a2a3a", fg="#a0a0c0", font=("Arial", 9))
        hint_label.pack(anchor="w", padx=5, pady=(0, 5))

        self.process_btn = tk.Button(self.root, text="Обработать", command=self.process_data,
                                     bg="#4a6fa5", fg="white", font=("Arial", 12, "bold"),
                                     activebackground="#5f8bc9", activeforeground="white",
                                     relief=tk.RAISED, padx=20, pady=5)
        self.process_btn.pack(pady=10)

        log_frame = tk.LabelFrame(self.root, text="Лог выполнения", bg="#2a2a3a", fg="white",
                                  font=("Arial", 10, "bold"), padx=5, pady=5)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, height=10, 
                                                  bg="#3a3a4a", fg="white", insertbackground="white")
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        clear_btn = tk.Button(self.root, text="Очистить лог", command=self.clear_log,
                              bg="#4a6fa5", fg="white", font=("Arial", 9))
        clear_btn.pack(pady=5)

        self.log("Интерфейс загружен.")
        self.log("Подсказка: используйте правую кнопку мыши для вырезания/копирования/вставки.")

    def log(self, message):
        """Вывод сообщения в лог"""
        if hasattr(self, 'log_text'):
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
            self.root.update_idletasks()
        else:
            print(message)

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def clear_input_text(self):
        self.input_text.delete(1.0, tk.END)

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def cut_text(self):
        try:
            selected = self.input_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
            self.input_text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def copy_text(self):
        try:
            selected = self.input_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass

    def paste_text(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.input_text.insert(tk.INSERT, clipboard_text)
        except tk.TclError:
            pass

    def process_data(self):
        data = self.input_text.get(1.0, tk.END).strip()
        if not data:
            self.log("Ошибка: поле ввода пусто.")
            messagebox.showwarning("Нет данных", "Пожалуйста, введите данные для обработки.")
            return

        lines = data.splitlines()
        products = []

        for idx, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            parts = re.split(r'\s+', line)
            if len(parts) < 3:
                self.log(f"Предупреждение: строка {idx} пропущена (некорректный формат): {line}")
                continue

            name_parts = parts[:-2]
            name = ' '.join(name_parts)
            price = parts[-2]
            try:
                quantity = int(parts[-1])
            except ValueError:
                self.log(f"Предупреждение: строка {idx} пропущена (количество не число): {line}")
                continue

            products.append([name, price, quantity])

        if not products:
            self.log("Нет корректных данных для обработки.")
            messagebox.showinfo("Нет данных", "Не найдено корректных записей.")
            return

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

        self.show_result_window(result_text)
        self.log("Операция завершена.")

    def show_result_window(self, result_text):
        result_win = tk.Toplevel(self.root)
        result_win.title("Результат обработки")
        result_win.geometry("500x400")
        result_win.configure(bg="#2a2a3a")
        result_win.resizable(True, True)

        result_win.update_idletasks()
        width = result_win.winfo_width()
        height = result_win.winfo_height()
        screen_width = result_win.winfo_screenwidth()
        screen_height = result_win.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        result_win.geometry(f'{width}x{height}+{x}+{y}')

        try:
            icon_path = resource_path("logo.ico")
            if os.path.exists(icon_path):
                result_win.iconbitmap(icon_path)
        except:
            pass

        frame = tk.LabelFrame(result_win, text="Сгруппированные данные", bg="#2a2a3a", fg="white",
                              font=("Arial", 10, "bold"), padx=5, pady=5)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        result_display = scrolledtext.ScrolledText(frame, wrap=tk.WORD, bg="#3a3a4a", fg="white",
                                                   insertbackground="white", font=("Arial", 10))
        result_display.insert(tk.END, result_text)
        result_display.config(state=tk.DISABLED)
        result_display.pack(fill="both", expand=True, padx=5, pady=5)

        close_btn = tk.Button(result_win, text="Закрыть", command=result_win.destroy,
                              bg="#4a6fa5", fg="white", font=("Arial", 10))
        close_btn.pack(pady=10)


if __name__ == "__main__":
    root = tk.Tk()
    app = ProductProcessorApp(root)
    root.mainloop()