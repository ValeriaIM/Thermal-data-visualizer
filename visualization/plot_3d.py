import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from scipy.interpolate import griddata
from visualization.plot_utils import PlotUtils

class Plot3D:
    def __init__(self):
        self.plot_utils = PlotUtils()
    
    def create_3d_plot_with_slice(self, data: pd.DataFrame, slice_params: dict, 
                                  show_isotherms=True, num_isotherms=10):
        """Создание нового 3D графика и среза в одном окне"""
        if not self.plot_utils.validate_data(data):
            raise ValueError("Некорректные данные для построения графика")
        
        # Включение интерактивного режима
        plt.ion()
        
        # Создание фигуры с двумя подграфиками
        fig = plt.figure(figsize=(15, 6))
        
        # Сохраняем ссылки на оси для последующего обновления
        ax1 = fig.add_subplot(121, projection='3d')
        ax2 = fig.add_subplot(122)
        
        # Сохраняем настройки изотерм
        fig.show_isotherms = show_isotherms
        fig.num_isotherms = num_isotherms
        
        # Создаем первоначальные графики
        self._update_3d_plot(ax1, data, slice_params)
        self._update_slice_plot(ax2, data, slice_params, show_isotherms, num_isotherms)
        
        plt.tight_layout()
        plt.show()
        
        # Сохраняем информацию о фигуре для последующего обновления
        fig.slices_axes = (ax1, ax2)
        fig.slice_params = slice_params.copy()
        fig.data = data
        
        return fig
    
    def update_3d_plot_with_slice(self, fig, data: pd.DataFrame, slice_params: dict, 
                                  show_isotherms=None, num_isotherms=None):
        """Обновление существующего графика со срезом"""
        if not fig or not hasattr(fig, 'slices_axes'):
            return self.create_3d_plot_with_slice(data, slice_params, show_isotherms, num_isotherms)
        
        # Обновляем настройки изотерм если переданы
        if show_isotherms is not None:
            fig.show_isotherms = show_isotherms
        if num_isotherms is not None:
            fig.num_isotherms = num_isotherms
        
        # Очищаем предыдущие графики
        ax1, ax2 = fig.slices_axes
        ax1.clear()
        ax2.clear()
        
        # Обновляем графики
        self._update_3d_plot(ax1, data, slice_params)
        self._update_slice_plot(ax2, data, slice_params, fig.show_isotherms, fig.num_isotherms)
        
        # Обновляем параметры
        fig.slice_params = slice_params.copy()
        fig.data = data
        
        # Перерисовываем фигуру
        fig.canvas.draw()
        fig.canvas.flush_events()
    
    def _update_3d_plot(self, ax, data: pd.DataFrame, slice_params: dict):
        """Обновление 3D графика"""
        # Используем pandas Series для доступа к данным
        x = data['x'].values
        y = data['y'].values
        z = data['z'].values
        T = data['T'].values
        
        # Расчет диапазона цветов
        color_range = self.plot_utils.calculate_color_range(T)
        
        # Создание scatter plot
        scatter = ax.scatter(x, y, z, c=T, cmap='viridis', s=20, alpha=0.6,
                           vmin=color_range['vmin'], vmax=color_range['vmax'])
        
        # Настройка 3D графика
        axis = slice_params['axis']
        value = slice_params['value']
        
        # Добавление плоскости среза на 3D график
        self._add_slice_plane(ax, data, axis, value)
        
        ax.set_xlabel('X Axis')
        ax.set_ylabel('Y Axis')
        ax.set_zlabel('Z Axis')
        ax.set_title(f'3D Scatter Plot\nСрез по {axis.upper()} = {value:.3f}')
        
        # Добавление цветовой шкалы
        if not hasattr(ax, 'colorbar') or ax.colorbar is None:
            ax.colorbar = plt.colorbar(scatter, ax=ax, shrink=0.6, aspect=20)
            ax.colorbar.set_label('Temperature (T)')
        else:
            # Обновляем существующую цветовую шкалу
            ax.colorbar.update_normal(scatter)
    
    def _update_slice_plot(self, ax, data: pd.DataFrame, slice_params: dict, 
                          show_isotherms=True, num_isotherms=10):
        """Обновление 2D среза с изотермами"""
        axis = slice_params['axis']
        value = slice_params['value']
        
        # Создание 2D среза
        slice_data = self._create_slice_data(data, axis, value)
        
        if slice_data is not None and len(slice_data) > 0:
            # Определяем координаты для графика в зависимости от оси среза
            if axis == 'x':
                x_coords = slice_data['y'].values
                y_coords = slice_data['z'].values
                x_label, y_label = 'Y Axis', 'Z Axis'
            elif axis == 'y':
                x_coords = slice_data['x'].values
                y_coords = slice_data['z'].values
                x_label, y_label = 'X Axis', 'Z Axis'
            else:  # z
                x_coords = slice_data['x'].values
                y_coords = slice_data['y'].values
                x_label, y_label = 'X Axis', 'Y Axis'
            
            temperatures = slice_data['T'].values
            
            # Создаем scatter plot точек
            sc = ax.scatter(x_coords, y_coords, c=temperatures, 
                           cmap='viridis', s=30, alpha=0.8, edgecolors='black', linewidth=0.5)
            
            # Добавляем изотермы если включено и достаточно точек
            if show_isotherms and len(temperatures) >= 10:
                self._add_isotherms(ax, x_coords, y_coords, temperatures, num_isotherms)
            
            ax.set_xlabel(x_label)
            ax.set_ylabel(y_label)
            ax.set_title(f'2D Срез по {axis.upper()} = {value:.3f}\n'
                         f'Точек в срезе: {len(slice_data)}')
            ax.grid(True, alpha=0.3)
            
            # Цветовая шкала для среза
            if not hasattr(ax, 'colorbar') or ax.colorbar is None:
                ax.colorbar = plt.colorbar(sc, ax=ax, shrink=0.8)
                ax.colorbar.set_label('Temperature (T)')
            else:
                ax.colorbar.update_normal(sc)
                
        else:
            ax.text(0.5, 0.5, 'Нет данных в выбранном срезе', 
                    ha='center', va='center', transform=ax.transAxes)
            ax.set_title(f'2D Срез по {axis.upper()} = {value:.3f}')
            # Убираем цветовую шкалу если нет данных
            if hasattr(ax, 'colorbar') and ax.colorbar:
                ax.colorbar.remove()
                ax.colorbar = None

    def _add_isotherms(self, ax, x, y, z, num_levels=10):
        """Добавление изотерм (контурных линий) на график"""
        try:
            # Очищаем предыдущие контуры
            for collection in ax.collections:
                if isinstance(collection, matplotlib.collections.PathCollection):
                    continue  # Пропускаем scatter точки
                collection.remove()
            
            for line in ax.lines:
                line.remove()
            
            # Создаем регулярную сетку для интерполяции
            xi = np.linspace(min(x), max(x), 100)
            yi = np.linspace(min(y), max(y), 100)
            Xi, Yi = np.meshgrid(xi, yi)
            
            # Интерполируем значения температуры на сетку
            Zi = griddata((x, y), z, (Xi, Yi), method='linear', fill_value=np.nan)
            
            # Убираем NaN значения для корректного построения контуров
            if np.any(~np.isnan(Zi)):
                # Создаем уровни для изотерм
                levels = np.linspace(np.nanmin(z), np.nanmax(z), num_levels)
                
                # Рисуем заполненные контуры (раскрашенные области)
                contourf = ax.contourf(Xi, Yi, Zi, levels=levels, alpha=0.3, cmap='viridis')
                
                # Рисуем линии контуров
                contours = ax.contour(Xi, Yi, Zi, levels=levels, colors='black', linewidths=0.5, alpha=0.7)
                
                # Добавляем подписи к контурным линиям
                #ax.clabel(contours, inline=True, fontsize=12, fmt='%.4f')
                labels = ax.clabel(contours, inline=True, fontsize=9, fmt='%.4f')
                if labels:
                    for txt in labels:
                        txt.set_fontweight('bold')
                
        except Exception as e:
            print(f"Ошибка при построении изотерм: {e}")
            # В случае ошибки просто рисуем точки без изотерм
    
    def _create_interpolated_grid(self, x, y, z, grid_size=100):
        """Создание интерполированной сетки для изотерм"""
        # Создаем регулярную сетку
        xi = np.linspace(np.min(x), np.max(x), grid_size)
        yi = np.linspace(np.min(y), np.max(y), grid_size)
        Xi, Yi = np.meshgrid(xi, yi)
        
        # Интерполируем значения на сетку
        Zi = griddata((x, y), z, (Xi, Yi), method='linear')
        
        return Xi, Yi, Zi
    
    def _add_slice_plane(self, ax, data: pd.DataFrame, axis: str, value: float, alpha=0.2):
        """Добавление плоскости среза на 3D график"""
        x_min, x_max = data['x'].min(), data['x'].max()
        y_min, y_max = data['y'].min(), data['y'].max()
        z_min, z_max = data['z'].min(), data['z'].max()
        
        if axis == 'x':
            # Плоскость YZ при фиксированном X
            yy, zz = np.meshgrid([y_min, y_max], [z_min, z_max])
            xx = np.full_like(yy, value)
            ax.plot_surface(xx, yy, zz, alpha=alpha, color='red')
        elif axis == 'y':
            # Плоскость XZ при фиксированном Y
            xx, zz = np.meshgrid([x_min, x_max], [z_min, z_max])
            yy = np.full_like(xx, value)
            ax.plot_surface(xx, yy, zz, alpha=alpha, color='red')
        else:  # z
            # Плоскость XY при фиксированном Z
            xx, yy = np.meshgrid([x_min, x_max], [y_min, y_max])
            zz = np.full_like(xx, value)
            ax.plot_surface(xx, yy, zz, alpha=alpha, color='red')
    
    def _create_slice_data(self, data: pd.DataFrame, axis: str, value: float, 
                          tolerance=0.1) -> pd.DataFrame:
        """Создание данных для среза с заданной точностью"""
        if axis == 'x':
            mask = np.abs(data['x'] - value) <= tolerance
        elif axis == 'y':
            mask = np.abs(data['y'] - value) <= tolerance
        else:  # z
            mask = np.abs(data['z'] - value) <= tolerance
        
        # Возвращаем DataFrame с отфильтрованными строками
        return data[mask].copy()