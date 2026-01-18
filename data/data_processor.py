import numpy as np

class DataProcessor:
    def __init__(self):
        pass
    
    def calculate_statistics(self, data):
        """Расчет статистики по данным"""
        if not data or not data['T']:
            return {}
        
        T_min = min(data['T'])
        T_max = max(data['T'])
        T_avg = np.mean(data['T'])
        
        return {
            'min': T_min,
            'max': T_max,
            'avg': T_avg,
            'count': len(data['x']),
            'x_range': (min(data['x']), max(data['x'])),
            'y_range': (min(data['y']), max(data['y'])),
            'z_range': (min(data['z']), max(data['z']))
        }
    
    def get_data_preview(self, data, num_points=10):
        """Получить превью данных"""
        preview_lines = []
        
        for i in range(min(num_points, len(data['x']))):
            preview_lines.append(
                f"Точка {i+1}: x={data['x'][i]:.6f}, "
                f"y={data['y'][i]:.6f}, z={data['z'][i]:.6f}, "
                f"T={data['T'][i]:.6f}"
            )
        
        return preview_lines
    
    def get_slice_data(self, data, axis, value, tolerance=0.1):
        """Получить данные для среза"""
        if axis == 'x':
            indices = [i for i, x in enumerate(data['x']) if abs(x - value) <= tolerance]
        elif axis == 'y':
            indices = [i for i, y in enumerate(data['y']) if abs(y - value) <= tolerance]
        elif axis == 'z':
            indices = [i for i, z in enumerate(data['z']) if abs(z - value) <= tolerance]
        else:
            return {}
        
        slice_data = {
            'x': [data['x'][i] for i in indices],
            'y': [data['y'][i] for i in indices],
            'z': [data['z'][i] for i in indices],
            'T': [data['T'][i] for i in indices]
        }
        
        return slice_data
