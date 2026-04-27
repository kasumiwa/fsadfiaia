import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime


class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("750x600")

        self.records = []
        self.file_name = "weather_diary.json"

        self.load_data()
        self.create_widgets()
        self.update_list()

    def create_widgets(self):
        main = ttk.Frame(self.root, padding="10")
        main.pack(fill=tk.BOTH, expand=True)

        input_frame = ttk.LabelFrame(main, text="Добавить запись", padding="10")
        input_frame.pack(fill=tk.X, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.date_entry = ttk.Entry(input_frame, width=20)
        self.date_entry.grid(row=0, column=1, pady=2, padx=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        ttk.Label(input_frame, text="Температура (°C):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.temp_entry = ttk.Entry(input_frame, width=20)
        self.temp_entry.grid(row=1, column=1, pady=2, padx=5)

        ttk.Label(input_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.desc_entry = ttk.Entry(input_frame, width=40)
        self.desc_entry.grid(row=2, column=1, pady=2, padx=5)

        ttk.Label(input_frame, text="Осадки:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.precip_var = tk.StringVar(value="Нет")
        ttk.Radiobutton(input_frame, text="Да", variable=self.precip_var, value="Да").grid(row=3, column=1, sticky=tk.W,
                                                                                           padx=5)
        ttk.Radiobutton(input_frame, text="Нет", variable=self.precip_var, value="Нет").grid(row=3, column=1,
                                                                                             sticky=tk.E, padx=50)

        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="Добавить запись", command=self.add_record).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Сохранить", command=self.save_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Загрузить", command=self.load_data).pack(side=tk.LEFT, padx=5)

        filter_frame = ttk.LabelFrame(main, text="Фильтрация", padding="10")
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Фильтр по дате:").grid(row=0, column=0, sticky=tk.W)
        self.filter_date = ttk.Entry(filter_frame, width=15)
        self.filter_date.grid(row=0, column=1, padx=5)
        self.filter_date.bind("<KeyRelease>", lambda e: self.update_list())

        ttk.Label(filter_frame, text="Температура выше (°C):").grid(row=1, column=0, sticky=tk.W)
        self.filter_temp = ttk.Entry(filter_frame, width=10)
        self.filter_temp.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.filter_temp.bind("<KeyRelease>", lambda e: self.update_list())

        ttk.Button(filter_frame, text="Сбросить фильтры", command=self.clear_filters).grid(row=2, column=1, sticky=tk.W,
                                                                                           pady=5)

        list_frame = ttk.LabelFrame(main, text="Записи о погоде", padding="10")
        list_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        columns = ("date", "temp", "description", "precipitation")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)

        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура")
        self.tree.heading("description", text="Описание")
        self.tree.heading("precipitation", text="Осадки")

        self.tree.column("date", width=100)
        self.tree.column("temp", width=80)
        self.tree.column("description", width=300)
        self.tree.column("precipitation", width=80)

        scroll = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

    def add_record(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой")
            return
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        try:
            datetime.strptime(date, "%Y-%m-%d")
        except:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return

        try:
            temp_float = float(temp)
        except:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        record = {
            "date": date,
            "temperature": temp_float,
            "description": desc,
            "precipitation": precip
        }

        self.records.append(record)
        self.records.sort(key=lambda x: x["date"])
        self.update_list()

        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)

        messagebox.showinfo("Успех", "Запись добавлена")

    def update_list(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        filter_date = self.filter_date.get().strip()
        filter_temp = self.filter_temp.get().strip()

        temp_threshold = None
        if filter_temp:
            try:
                temp_threshold = float(filter_temp)
            except:
                pass

        for record in self.records:
            if filter_date and record["date"] != filter_date:
                continue
            if temp_threshold is not None and record["temperature"] <= temp_threshold:
                continue

            self.tree.insert("", tk.END, values=(
                record["date"],
                f"{record['temperature']}°C",
                record["description"],
                record["precipitation"]
            ))

    def clear_filters(self):
        self.filter_date.delete(0, tk.END)
        self.filter_temp.delete(0, tk.END)
        self.update_list()

    def save_data(self):
        try:
            with open(self.file_name, 'w', encoding='utf-8') as f:
                json.dump(self.records, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "Данные сохранены")
        except:
            messagebox.showerror("Ошибка", "Не удалось сохранить")

    def load_data(self):
        if os.path.exists(self.file_name):
            try:
                with open(self.file_name, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
                self.records.sort(key=lambda x: x["date"])
                self.update_list()
                messagebox.showinfo("Успех", "Данные загружены")
            except:
                messagebox.showerror("Ошибка", "Не удалось загрузить")
        else:
            messagebox.showwarning("Нет файла", "Файл с данными не найден")


if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()