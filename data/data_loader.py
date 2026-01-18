import csv

class DataLoader:
    def __init__(self):
        pass
    
    def load_from_csv(self, file_path):
        """Загрузка данных из CSV файла"""
        with open(file_path, 'r', encoding='utf-8') as file:
            csv_reader = csv.reader(file)
            lines = list(csv_reader)
        
        return self.parse_csv_data(lines)

    def load_from_dat(self, file_path):
        """Загрузка данных из DAT файла"""
        # Читаем файл
        with open(input_file, 'r') as file:
            lines = file.readlines()
        
        # Пропускаем служебные строки (до данных)
        data_lines = []
        for line in lines:
            # Ищем строки, которые начинаются с числа (данные)
            if line.strip() and (line.strip()[0].isdigit() or line.strip()[0] == '-'):
                data_lines.append(line.strip())

            # Разбиваем данные на столбцы
        data = []
        for line in data_lines:
            # Разделяем по пробелам и фильтруем пустые значения
            values = [x for x in line.split() if x]
            data.append(values)
        
        # Создаем DataFrame
        df = pd.DataFrame(data, columns=['x', 'y', 'z', 'T'])
        
        # Преобразуем столбцы к числовым типам
        df['x'] = pd.to_numeric(df['x'])
        df['y'] = pd.to_numeric(df['y'])
        df['z'] = pd.to_numeric(df['z'])
        df['T'] = pd.to_numeric(df['T'])
        
        # Округляем координаты до целых чисел
        df['x_rounded'] = df['x'].round().astype(int)
        df['y_rounded'] = df['y'].round().astype(int)
        df['z_rounded'] = df['z'].round().astype(int)
        
        # Группируем по округленным координатам и вычисляем среднюю температуру
        grouped_df = df.groupby(['x_rounded', 'y_rounded', 'z_rounded'])['T'].mean().reset_index()
        
        # Переименовываем столбцы обратно
        grouped_df = grouped_df.rename(columns={
            'x_rounded': 'x',
            'y_rounded': 'y', 
            'z_rounded': 'z'
        })

        return grouped_df

    
    def parse_csv_data(self, lines):
        """Парсинг данных из CSV файла"""
        data = {'x': [], 'y': [], 'z': [], 'T': []}
        
        for i, row in enumerate(lines):
            # Пропускаем пустые строки
            if not row:
                continue
                
            # Пропускаем строки с комментариями
            if any(cell.strip().startswith('#') for cell in row if cell.strip()):
                continue
                
            try:
                # Проверяем, есть ли заголовок (первая строка)
                if i == 0:
                    if all(cell.strip().lower() in ['x', 'y', 'z', 't'] for cell in row[:4]):
                        continue  # Пропускаем строку заголовка
                
                # Обрабатываем данные
                if len(row) >= 4:
                    data['x'].append(float(row[0]))
                    data['y'].append(float(row[1]))
                    data['z'].append(float(row[2]))
                    data['T'].append(float(row[3]))
                    
            except (ValueError, IndexError) as e:
                print(f"Пропущена строка {i+1}: {row} - ошибка: {e}")
        
        return data