import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os

class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner - План тренировок")
        self.root.geometry("800x600")
        
        # Файл для хранения данных
        self.data_file = "trainings.json"
        self.trainings = []
        
        # Загрузка существующих данных
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
    def create_widgets(self):
        # Фрейм для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding="10")
        input_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")
        
        # Поля ввода
        ttk.Label(input_frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=0, column=0, sticky="w", pady=2)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=2)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        
        ttk.Label(input_frame, text="Тип тренировки:").grid(row=1, column=0, sticky="w", pady=2)
        self.type_combo = ttk.Combobox(input_frame, width=18, values=[
            "Бег", "Плавание", "Велосипед", "Силовая", "Йога", 
            "Кроссфит", "Растяжка", "Бокс", "Танцы", "Другое"
        ])
        self.type_combo.grid(row=1, column=1, padx=5, pady=2)
        self.type_combo.set("Бег")
        
        ttk.Label(input_frame, text="Длительность (минут):").grid(row=2, column=0, sticky="w", pady=2)
        self.duration_entry = ttk.Entry(input_frame, width=20)
        self.duration_entry.grid(row=2, column=1, padx=5, pady=2)
        
        # Кнопка добавления
        self.add_button = ttk.Button(input_frame, text="Добавить тренировку", 
                                     command=self.add_training)
        self.add_button.grid(row=3, column=0, columnspan=2, pady=10)
        
        # Фрейм для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding="10")
        filter_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Label(filter_frame, text="По типу:").grid(row=0, column=0, sticky="w")
        self.filter_type = ttk.Combobox(filter_frame, width=18, values=["Все"] + [
            "Бег", "Плавание", "Велосипед", "Силовая", "Йога", 
            "Кроссфит", "Растяжка", "Бокс", "Танцы", "Другое"
        ])
        self.filter_type.grid(row=0, column=1, padx=5)
        self.filter_type.set("Все")
        self.filter_type.bind("<<ComboboxSelected>>", self.apply_filters)
        
        ttk.Label(filter_frame, text="По дате (с):").grid(row=0, column=2, sticky="w")
        self.filter_date_from = ttk.Entry(filter_frame, width=12)
        self.filter_date_from.grid(row=0, column=3, padx=2)
        
        ttk.Label(filter_frame, text="по:").grid(row=0, column=4, sticky="w")
        self.filter_date_to = ttk.Entry(filter_frame, width=12)
        self.filter_date_to.grid(row=0, column=5, padx=2)
        
        self.filter_button = ttk.Button(filter_frame, text="Применить фильтр", 
                                        command=self.apply_filters)
        self.filter_button.grid(row=0, column=6, padx=5)
        
        self.reset_filter_button = ttk.Button(filter_frame, text="Сбросить", 
                                             command=self.reset_filters)
        self.reset_filter_button.grid(row=0, column=7, padx=5)
        
        # Таблица для отображения тренировок
        table_frame = ttk.LabelFrame(self.root, text="Список тренировок", padding="10")
        table_frame.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        
        # Создание Treeview
        columns = ("date", "type", "duration")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("date", text="Дата")
        self.tree.heading("type", text="Тип тренировки")
        self.tree.heading("duration", text="Длительность (мин)")
        
        self.tree.column("date", width=120)
        self.tree.column("type", width=200)
        self.tree.column("duration", width=150)
        
        # Добавление скроллбара
        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Кнопка удаления
        self.delete_button = ttk.Button(table_frame, text="Удалить выбранную тренировку", 
                                       command=self.delete_training)
        self.delete_button.grid(row=1, column=0, pady=5)
        
        # Настройка весов для ресайза
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Обновление таблицы
        self.refresh_table()
    
    def validate_input(self):
        """Проверка корректности ввода"""
        date_str = self.date_entry.get()
        try:
            datetime.strptime(date_str, "%d.%m.%Y")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ДД.ММ.ГГГГ")
            return False
        
        if not self.type_combo.get():
            messagebox.showerror("Ошибка", "Выберите тип тренировки")
            return False
        
        try:
            duration = int(self.duration_entry.get())
            if duration <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Длительность должна быть положительным целым числом")
            return False
        
        return True
    
    def add_training(self):
        """Добавление новой тренировки"""
        if not self.validate_input():
            return
        
        training = {
            "date": self.date_entry.get(),
            "type": self.type_combo.get(),
            "duration": int(self.duration_entry.get())
        }
        
        self.trainings.append(training)
        self.save_data()
        self.refresh_table()
        
        # Очистка полей (кроме даты)
        self.type_combo.set("Бег")
        self.duration_entry.delete(0, tk.END)
        
        messagebox.showinfo("Успех", "Тренировка добавлена!")
    
    def delete_training(self):
        """Удаление выбранной тренировки"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Предупреждение", "Выберите тренировку для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить эту тренировку?"):
            item = selected_item[0]
            values = self.tree.item(item)["values"]
            
            # Поиск и удаление тренировки
            for i, training in enumerate(self.trainings):
                if (training["date"] == values[0] and 
                    training["type"] == values[1] and 
                    training["duration"] == int(values[2])):
                    del self.trainings[i]
                    break
            
            self.save_data()
            self.refresh_table()
    
    def apply_filters(self, event=None):
        """Применение фильтров к таблице"""
        self.refresh_table()
    
    def reset_filters(self):
        """Сброс фильтров"""
        self.filter_type.set("Все")
        self.filter_date_from.delete(0, tk.END)
        self.filter_date_to.delete(0, tk.END)
        self.refresh_table()
    
    def get_filtered_trainings(self):
        """Получение отфильтрованного списка тренировок"""
        filtered = self.trainings.copy()
        
        # Фильтр по типу
        filter_type = self.filter_type.get()
        if filter_type != "Все":
            filtered = [t for t in filtered if t["type"] == filter_type]
        
        # Фильтр по дате
        date_from = self.filter_date_from.get()
        date_to = self.filter_date_to.get()
        
        if date_from:
            try:
                from_date = datetime.strptime(date_from, "%d.%m.%Y")
                filtered = [t for t in filtered if datetime.strptime(t["date"], "%d.%m.%Y") >= from_date]
            except ValueError:
                pass
        
        if date_to:
            try:
                to_date = datetime.strptime(date_to, "%d.%m.%Y")
                filtered = [t for t in filtered if datetime.strptime(t["date"], "%d.%m.%Y") <= to_date]
            except ValueError:
                pass
        
        # Сортировка по дате (новые сверху)
        filtered.sort(key=lambda x: datetime.strptime(x["date"], "%d.%m.%Y"), reverse=True)
        
        return filtered
    
    def refresh_table(self):
        """Обновление таблицы"""
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Добавление отфильтрованных данных
        for training in self.get_filtered_trainings():
            self.tree.insert("", tk.END, values=(
                training["date"],
                training["type"],
                training["duration"]
            ))
    
    def save_data(self):
        """Сохранение данных в JSON файл"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.trainings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка сохранения", f"Не удалось сохранить данные: {str(e)}")
    
    def load_data(self):
        """Загрузка данных из JSON файла"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.trainings = json.load(f)
            except Exception as e:
                messagebox.showwarning("Предупреждение", f"Не удалось загрузить данные: {str(e)}")
                self.trainings = []
        else:
            self.trainings = []

def main():
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
