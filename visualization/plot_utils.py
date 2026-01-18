import matplotlib.pyplot as plt
import numpy as np
from typing import List, Dict, Any

class PlotUtils:
    @staticmethod
    def enable_interactive_mode():
        """Включение интерактивного режима matplotlib"""
        plt.ion()
    
    @staticmethod
    def disable_interactive_mode():
        """Выключение интерактивного режима matplotlib"""
        plt.ioff()
        
    @staticmethod
    def calculate_color_range(temperatures: List[float]) -> Dict[str, float]:
        """Расчет оптимального диапазона цветов для визуализации"""
        T_min = min(temperatures)
        T_max = max(temperatures)
        T_avg = np.mean(temperatures)
        
        # Настройка диапазона цветов для лучшей визуализации
        vmin = T_avg - 2 * (T_avg - T_min) / 10
        vmax = T_avg + 2 * (T_max - T_avg) / 10
        
        return {
            'vmin': vmin,
            'vmax': vmax,
            'min': T_min,
            'max': T_max,
            'avg': T_avg
        }
    
    @staticmethod
    def get_colormap_options() -> Dict[str, str]:
        """Доступные цветовые карты"""
        return {
            'viridis': 'Viridis (по умолчанию)',
            'plasma': 'Plasma',
            'inferno': 'Inferno',
            'magma': 'Magma',
            'coolwarm': 'Cool-Warm',
            'rainbow': 'Rainbow',
            'jet': 'Jet'
        }
    
    @staticmethod
    def validate_data(data: Dict[str, List[float]]) -> bool:
        """Проверка корректности данных для построения графика"""
        required_keys = ['x', 'y', 'z', 'T']
        
        # Проверяем наличие всех необходимых ключей
        if not all(key in data for key in required_keys):
            return False
        
        # Проверяем, что все массивы одинаковой длины
        lengths = [len(data[key]) for key in required_keys]
        if len(set(lengths)) != 1:
            return False
        
        # Проверяем, что есть хотя бы одна точка
        if lengths[0] == 0:
            return False
        
        return True
    
    @staticmethod
    def create_figure(size: tuple = (12, 8)) -> tuple:
        """Создание фигуры с настройками по умолчанию"""
        fig = plt.figure(figsize=size)
        return fig, fig.add_subplot(111, projection='3d')
    
    @staticmethod
    def setup_plot(ax, data: Dict[str, List[float]], title: str = ""):
        """Настройка осей и заголовка графика"""
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')
        
        if title:
            ax.set_title(title)
        else:
            T_min = min(data['T'])
            T_max = max(data['T'])
            ax.set_title(f'3D Scatter Plot with Temperature Coloring\n'
                        f'Points: {len(data["x"]):,}, T-range: [{T_min:.3f}, {T_max:.3f}]')
    
    @staticmethod
    def add_colorbar(fig, scatter, label: str = 'Temperature (T)'):
        """Добавление цветовой шкалы"""
        cbar = plt.colorbar(scatter, shrink=0.5, aspect=20)
        cbar.set_label(label)
        return cbar

    @staticmethod
    def show_temperature_histogram(temperatures: List[float], bins: int = 50):
        """Показать гистограмму распределения температур"""
        plt.figure(figsize=(10, 6))
        plt.hist(temperatures, bins=bins, alpha=0.7, color='blue', edgecolor='black')
        plt.xlabel('Temperature')
        plt.ylabel('Frequency')
        plt.title('Distribution of Temperature Values')
        plt.grid(True, alpha=0.3)
        
        # Добавляем вертикальные линии для статистики
        mean_temp = np.mean(temperatures)
        min_temp = np.min(temperatures)
        max_temp = np.max(temperatures)
        
        plt.axvline(mean_temp, color='red', linestyle='--', 
                   label=f'Mean: {mean_temp:.3f}')
        plt.axvline(min_temp, color='green', linestyle='--', 
                   label=f'Min: {min_temp:.3f}')
        plt.axvline(max_temp, color='orange', linestyle='--', 
                   label=f'Max: {max_temp:.3f}')
        
        plt.legend()
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def save_plot(filename: str, dpi: int = 300):
        """Сохранение текущего графика в файл"""
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        print(f"График сохранен как: {filename}")
