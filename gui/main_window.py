import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from data.data_loader import DataLoader
from visualization.plot_3d import Plot3D
from utils.file_utils import FileUtils
import pandas as pd
import numpy as np

class Graph3DApp:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Graph Viewer")
        self.root.geometry("700x750") # ширина х высота
        
        self.data_loader = DataLoader()
        self.plot_3d = Plot3D()
        self.file_utils = FileUtils()
        
        self.data = None
        self.slice_value = tk.DoubleVar(value=0.0)
        self.slice_axis = tk.StringVar(value="z")
        self.show_isotherms = tk.BooleanVar(value=True)
        self.num_isotherms = tk.IntVar(value=10)
        self.current_figure = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Заголовок
        title_label = tk.Label(self.root, text="3D Graph Viewer", 
                              font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # Фрейм для кнопок
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)
        
        # Кнопка загрузки данных
        self.load_btn = tk.Button(button_frame, text="Загрузить данные", 
                                 command=self.load_data,
                                 bg="lightblue", font=("Arial", 12))
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка построения графика
        self.plot_btn = tk.Button(button_frame, text="Построить график", 
                                 command=self.plot_3d_graph,
                                 bg="lightgreen", font=("Arial", 12))
        self.plot_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка обновления графика
        self.update_btn = tk.Button(button_frame, text="Обновить график", 
                                   command=self.update_plot,
                                   bg="lightcoral", font=("Arial", 12))
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        # Кнопка создания примера файла
        self.example_btn = tk.Button(button_frame, text="Создать пример файла", 
                                    command=self.create_example_file,
                                    bg="lightyellow", font=("Arial", 12))
        self.example_btn.pack(side=tk.LEFT, padx=5)
        
        # Фрейм для управления срезом
        slice_frame = tk.LabelFrame(self.root, text="Управление срезом", font=("Arial", 10))
        slice_frame.pack(pady=10, padx=20, fill=tk.X)
        
        # Выбор оси среза
        axis_frame = tk.Frame(slice_frame)
        axis_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(axis_frame, text="Ось среза:", font=("Arial", 9)).pack(side=tk.LEFT)
        
        tk.Radiobutton(axis_frame, text="X", variable=self.slice_axis, 
                      value="x", command=self.on_slice_change).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(axis_frame, text="Y", variable=self.slice_axis, 
                      value="y", command=self.on_slice_change).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(axis_frame, text="Z", variable=self.slice_axis, 
                      value="z", command=self.on_slice_change).pack(side=tk.LEFT, padx=5)
        
        # Поле ввода и ползунок для значения среза
        value_frame = tk.Frame(slice_frame)
        value_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(value_frame, text="Значение среза:", font=("Arial", 9)).pack(side=tk.LEFT)
        
        self.slice_entry = tk.Entry(value_frame, textvariable=self.slice_value, 
                                   width=10, font=("Arial", 9))
        self.slice_entry.pack(side=tk.LEFT, padx=5)
        self.slice_entry.bind('<Return>', self.on_slice_entry_change)
        
        self.slice_slider = tk.Scale(value_frame, from_=0, to=100, 
                                    orient=tk.HORIZONTAL, variable=self.slice_value,
                                    command=self.on_slider_change, length=300)
        self.slice_slider.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # Фрейм для настроек изотерм
        isotherm_frame = tk.LabelFrame(self.root, text="Настройки изотерм", font=("Arial", 10))
        isotherm_frame.pack(pady=5, padx=20, fill=tk.X)
        
        isotherm_settings_frame = tk.Frame(isotherm_frame)
        isotherm_settings_frame.pack(fill=tk.X, pady=5)
        
        # Чекбокс для показа изотерм
        self.isotherm_check = tk.Checkbutton(isotherm_settings_frame, text="Показать изотермы",
                                           variable=self.show_isotherms,
                                           command=self.on_isotherm_settings_change)
        self.isotherm_check.pack(side=tk.LEFT, padx=5)
        
        # Количество изотерм
        tk.Label(isotherm_settings_frame, text="Количество изотерм:", font=("Arial", 9)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.isotherm_spin = tk.Spinbox(isotherm_settings_frame, from_=3, to=50, 
                                  textvariable=self.num_isotherms, width=5,
                                  command=self.on_isotherm_settings_change)
        self.isotherm_spin.pack(side=tk.LEFT, padx=5)

        # Привязываем событие изменения текста в Spinbox
        self.isotherm_spin.bind('<KeyRelease>', self.on_isotherm_spin_change)
        
        # Область для отображения информации
        self.info_text = tk.Text(self.root, height=12, width=70, font=("Courier", 10))
        self.info_text.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = tk.Label(self.root, textvariable=self.status_var, 
                             relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def on_isotherm_settings_change(self):
        """Обработчик изменения настроек изотерм"""
        if self.data is not None and self.current_figure:
            self.update_plot()

    def on_isotherm_spin_change(self, event=None):
        """Обработчик ручного ввода в Spinbox"""
        try:
            # Пытаемся преобразовать значение в integer
            value = int(self.isotherm_spin.get())
            if 3 <= value <= 50:  # Проверяем диапазон
                self.num_isotherms.set(value)
                if self.data is not None and self.current_figure:
                    self.update_plot()
        except ValueError:
            # Игнорируем некорректный ввод
            pass
    
    def on_slice_change(self):
        """Обработчик изменения оси среза"""
        if self.data is not None:
            self.update_slider_range()
            self.show_slice_info()
            if self.current_figure:
                self.update_plot()
    
    def on_slice_entry_change(self, event=None):
        """Обработчик изменения значения в поле ввода"""
        try:
            value = float(self.slice_entry.get())
            self.slice_value.set(value)
            self.show_slice_info()
            if self.data is not None and self.current_figure:
                self.update_plot()
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное числовое значение")
    
    def on_slider_change(self, value):
        """Обработчик изменения ползунка"""
        if self.data is not None and self.current_figure:
            self.update_plot()
    
    def update_slider_range(self):
        """Обновление диапазона ползунка в зависимости от данных и выбранной оси"""
        if self.data is None:
            return
            
        axis = self.slice_axis.get()
        min_val = self.data[axis].min()
        max_val = self.data[axis].max()
        
        self.slice_slider.config(from_=min_val, to=max_val)
        # Устанавливаем среднее значение по умолчанию
        self.slice_value.set((min_val + max_val) // 2)
    
    def load_data(self):
        """Загрузка данных из CSV файла"""
        file_path = filedialog.askopenfilename(
            title="Выберите DAT или CSV файл с данными",
            filetypes=[("DAT files", "*.dat"), ("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.data = self.data_loader.load_data(file_path)
                self.show_data_info()
                self.update_slider_range()
                self.show_slice_info()
                self.status_var.set(f"Данные загружены из: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {str(e)}")
                self.status_var.set("Ошибка загрузки данных")
    
    def show_data_info(self):
        """Отображение информации о загруженных данных"""
        if self.data is not None and not self.data.empty:
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, "Загруженные данные:\n")
            self.info_text.insert(tk.END, "="*50 + "\n")
            
            # Показываем первые 5 точек
            preview_data = self.data.head(5)
            self.info_text.insert(tk.END, preview_data.to_string() + "\n")
            
            # Добавляем статистику
            T_min = self.data['T'].min()
            T_max = self.data['T'].max()
            T_mean = self.data['T'].mean()
            self.info_text.insert(tk.END, f"\nВсего точек: {len(self.data['x'])}\n")
            self.info_text.insert(tk.END, 
                f"Температура: мин={T_min:.3f}, макс={T_max:.3f}, средн={T_mean:.3f}\n")

    def show_slice_info(self):
        """Отображение информации о загруженных данных"""
        if self.data is not None and not self.data.empty:
            axis = self.slice_axis.get()
            value = float(self.slice_value.get())
            self.info_text.insert(tk.END, "\n" + "="*50 + "\n")
            self.info_text.insert(tk.END, f"\nИнформация по срезу. Ось: {axis.upper()}, значение: {value:.3f}\n")


            slice_data = self.get_slice_data(axis, value)

            if slice_data is not None and len(slice_data) > 0:
                # Статистика по точкам в срезе
                T_min = slice_data['T'].min()
                T_max = slice_data['T'].max()
                T_mean = slice_data['T'].mean()
                T_std = slice_data['T'].std()
                
                self.info_text.insert(tk.END, "\nСТАТИСТИКА ТЕМПЕРАТУР:\n")
                self.info_text.insert(tk.END, f"  Всего точек в срезе: {len(slice_data)}\n")
                self.info_text.insert(tk.END, f"  Минимальная: {T_min:.3f}\n")
                self.info_text.insert(tk.END, f"  Максимальная: {T_max:.3f}\n")
                self.info_text.insert(tk.END, f"  Средняя: {T_mean:.3f}\n")
                self.info_text.insert(tk.END, f"  Стандартное отклонение: {T_std:.3f}\n")

            else:
                self.info_text.insert(tk.END, "СРЕЗ НЕ СОДЕРЖИТ ДАННЫХ\n")
                self.info_text.insert(tk.END, "="*50 + "\n")
                self.info_text.insert(tk.END, "\nНет точек в выбранном срезе.\n")
                self.info_text.insert(tk.END, "Попробуйте изменить значение или ось.\n")
            

    def get_slice_data(self, axis, value, tolerance=0.1):
        """Получение данных для среза по заданной оси и значению"""
        if self.data is None or self.data.empty:
            return None
        
        # Создаем маску для фильтрации точек в срезе
        if axis == 'x':
            mask = np.abs(self.data['x'] - value) <= tolerance
        elif axis == 'y':
            mask = np.abs(self.data['y'] - value) <= tolerance
        else:  # axis == 'z'
            mask = np.abs(self.data['z'] - value) <= tolerance
        
        return self.data[mask].copy()

    def plot_3d_graph(self):
        """Создание нового 3D графика со срезом"""
        if self.data is None or len(self.data['x']) == 0:
            messagebox.showwarning("Предупреждение", "Сначала загрузите данные!")
            return
        
        try:
            slice_params = {
                'axis': self.slice_axis.get(),
                'value': self.slice_value.get()
            }
            
            self.current_figure = self.plot_3d.create_3d_plot_with_slice(
                self.data, 
                slice_params,
                show_isotherms=self.show_isotherms.get(),
                num_isotherms=self.num_isotherms.get()
            )
            self.status_var.set("3D график и срез построены успешно")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось построить график: {str(e)}")
            self.status_var.set("Ошибка построения графика")
    
    def update_plot(self):
        """Обновление существующего графика"""
        if self.data is None or not self.current_figure:
            return
        
        try:
            slice_params = {
                'axis': self.slice_axis.get(),
                'value': self.slice_value.get()
            }
            
            self.plot_3d.update_3d_plot_with_slice(
                self.current_figure, 
                self.data, 
                slice_params,
                show_isotherms=self.show_isotherms.get(),
                num_isotherms=self.num_isotherms.get()
            )
            self.status_var.set(f"График обновлен. Срез по {slice_params['axis'].upper()} = {slice_params['value']:.3f}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить график: {str(e)}")
            self.status_var.set("Ошибка обновления графика")
    
    def create_example_file(self):
        """Создание примера CSV файла с данными"""
        file_path = filedialog.asksaveasfilename(
            title="Сохранить пример CSV файла",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")]
        )
        
        if file_path:
            try:
                self.file_utils.create_example_csv(file_path)
                messagebox.showinfo("Успех", f"Пример CSV файла создан: {file_path}")
                self.status_var.set(f"Пример файла создан: {os.path.basename(file_path)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось создать файл: {str(e)}")
