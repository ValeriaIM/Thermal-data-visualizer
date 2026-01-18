import pandas as pd
import numpy as np

class DataLoader:
    def __init__(self):
        pass
    
    def load_from_csv(self, file_path):
        """Загрузка данных из CSV файла с использованием pandas"""
        try:
            # Сначала попробуем прочитать с заголовком
            try:
                # Пробуем прочитать с заголовком
                df = pd.read_csv(
                    file_path,
                    comment='#',
                    skip_blank_lines=True,
                    header=0,  # Первая строка - заголовок
                    encoding='utf-8',
                    on_bad_lines='warn'
                )
                
                # Проверяем, есть ли нужные колонки (регистронезависимо)
                df.columns = df.columns.str.strip().str.lower()
                expected_columns = ['x', 'y', 'z', 't']
                
                # Проверяем наличие необходимых столбцов
                if all(col in df.columns for col in expected_columns):
                    # Оставляем только нужные колонки и переименовываем
                    df = df[expected_columns].copy()
                    df.columns = ['x', 'y', 'z', 'T']
                else:
                    # Если нужных колонок нет, возможно это данные без заголовка
                    raise ValueError("Заголовок не содержит ожидаемых колонок")
                    
            except (ValueError, pd.errors.ParserError):
                # Читаем как данные без заголовка
                df = pd.read_csv(
                    file_path,
                    comment='#',
                    skip_blank_lines=True,
                    header=None,  # Нет заголовка
                    names=['x', 'y', 'z', 'T'],  # Имена столбцов
                    encoding='utf-8',
                    on_bad_lines='warn'
                )
            
            # Преобразуем столбцы к числовым типам
            for col in ['x', 'y', 'z', 'T']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Удаляем строки с NaN значениями
            df = df.dropna()
            
            # Проверяем, есть ли данные
            if len(df) == 0:
                print(f"Предупреждение: файл {file_path} не содержит числовых данных")
            
            return df
            
        except Exception as e:
            print(f"Ошибка при загрузке CSV файла {file_path}: {e}")
            return pd.DataFrame(columns=['x', 'y', 'z', 'T'])
    
    def load_from_dat(self, file_path, fl_binning = False, bin_width_x=0.5, bin_width_y=0.5, bin_width_z=0.5):
        """Загрузка данных из DAT файла"""
        try:
            # Читаем файл построчно
            with open(file_path, 'r') as file:
                lines = file.readlines()
            
            # Фильтруем строки, которые начинаются с числа или минуса (данные)
            data_lines = []
            for line in lines:
                stripped = line.strip()
                if stripped and (stripped[0].isdigit() or stripped[0] == '-'):
                    data_lines.append(stripped)
            
            # Если нет данных, возвращаем пустой DataFrame
            if not data_lines:
                return pd.DataFrame(columns=['x', 'y', 'z', 'T'])
            
            # Создаем DataFrame из отфильтрованных строк
            # Используем регулярное выражение для разделения по пробелам
            df = pd.DataFrame([line.split() for line in data_lines])
            print(f"Есть {len(df)} записей в DAT")
            
            # Обрабатываем разное количество столбцов
            if df.shape[1] >= 4:
                df = df.iloc[:, :4]  # Берем только первые 4 столбца
                df.columns = ['x', 'y', 'z', 'T']
            else:
                raise ValueError(f"Недостаточно столбцов в данных. Найдено: {df.shape[1]}")
            
            # Преобразуем к числовым типам
            numeric_cols = ['x', 'y', 'z', 'T']
            for col in numeric_cols:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Удаляем строки с NaN после преобразования
            df = df.dropna()
            
            if fl_binning:
                return get_data_with_binning(df, bin_width_x, bin_width_y, bin_width_z)
            else:
                return get_mean_temp_by_rounded_data(df)

            
        except Exception as e:
            print(f"Ошибка при загрузке DAT файла: {e}")
            return pd.DataFrame(columns=['x', 'y', 'z', 'T'])
    
    def load_data(self, file_path):
        """Универсальный метод загрузки данных по расширению файла"""
        if file_path.endswith('.csv'):
            return self.load_from_csv(file_path)
        elif file_path.endswith('.dat'):
            return self.load_from_dat(file_path)
        else:
            raise ValueError(f"Неподдерживаемый формат файла: {file_path}")

    def save_to_csv(self, df, file_path):
        """Сохранение DataFrame в CSV файл"""
        if not isinstance(df, pd.DataFrame):
            raise TypeError("Данные должны быть pandas DataFrame")
        
        df.to_csv(file_path, index=False, encoding='utf-8')
        print(f"Данные сохранены в {file_path}")

    def get_data_without_binning(df):
        '''
        Для прореживания точек использует 
        округление и группировку коорединат
        с взятием средней температуры
        '''
        # Округляем координаты и группируем
        rounded_cols = ['x_rounded', 'y_rounded', 'z_rounded']
        for i, col in enumerate(['x', 'y', 'z']):
            df[rounded_cols[i]] = df[col].round().astype(int)
        
        # Группируем по округленным координатам
        grouped_df = df.groupby(
            ['x_rounded', 'y_rounded', 'z_rounded'],
            as_index=False
        )['T'].mean()
        
        # Переименовываем столбцы
        grouped_df = grouped_df.rename(columns={
            'x_rounded': 'x',
            'y_rounded': 'y', 
            'z_rounded': 'z'
        })
        
        return grouped_df

    def get_data_with_binning(df, bin_width_x=0.5, bin_width_y=0.5, bin_width_z=0.5):
        """
        Для прореживания точек использует бинирование.

        Параметры:
        ----------
        bin_width_x, bin_width_y, bin_width_z : float
            Ширина бинов по каждой оси (по умолчанию 0,5)
        """
        # ВАРИАНТ 1: Биннинг с вычислением центроидов бинов
        # Создаем бины для каждой оси
        x_min, x_max = df['x'].min(), df['x'].max()
        y_min, y_max = df['y'].min(), df['y'].max()
        z_min, z_max = df['z'].min(), df['z'].max()

        # Вычисляем количество бинов
        num_bins_x = int(np.ceil((x_max - x_min) / bin_width_x)) + 1
        num_bins_y = int(np.ceil((y_max - y_min) / bin_width_y)) + 1
        num_bins_z = int(np.ceil((z_max - z_min) / bin_width_z)) + 1

        print(f"Количество бинов: X={num_bins_x}, Y={num_bins_y}, Z={num_bins_z}")

        # Присваиваем каждой точке номер бина
        df['x_bin'] = ((df['x'] - x_min) // bin_width_x).astype(int)
        df['y_bin'] = ((df['y'] - y_min) // bin_width_y).astype(int)
        df['z_bin'] = ((df['z'] - z_min) // bin_width_z).astype(int)

        # Группируем по бинам и вычисляем средние значения
        grouped_df = df.groupby(['x_bin', 'y_bin', 'z_bin']).agg({
            'T': 'mean',
            'x': 'mean',  # Можно также использовать 'first', 'min', 'max' или вычислять центроид
            'y': 'mean',
            'z': 'mean'
        }).reset_index()

        # Переименовываем столбцы
        grouped_df = grouped_df.rename(columns={
            'x': 'x_centroid',
            'y': 'y_centroid',
            'z': 'z_centroid'
        })

        # ВАРИАНТ 2: Альтернативный подход - вычисление центров бинов
        # Этот вариант создает равномерную сетку с центрами бинов
        # def calculate_bin_centers(df, coord_col, min_val, bin_width):
        #     """Вычисляет центры бинов на основе номеров бинов"""
        #     return min_val + (df[f'{coord_col}_bin'] + 0.5) * bin_width
        #
        # # Добавляем центры бинов
        # grouped_df['x_center'] = calculate_bin_centers(grouped_df, 'x', x_min, bin_width_x)
        # grouped_df['y_center'] = calculate_bin_centers(grouped_df, 'y', y_min, bin_width_y)
        # grouped_df['z_center'] = calculate_bin_centers(grouped_df, 'z', z_min, bin_width_z)

        # Выбираем нужные столбцы для сохранения
        # Можно выбрать либо центроиды (реальные средние координаты), либо центры бинов (равномерная сетка)
        # Поменять *_x_centroid -> *_center и раскомитеть сверху
        result_df = grouped_df[['x_centroid', 'y_centroid', 'z_centroid', 'T']].copy()
        result_df = result_df.rename(columns={
            'x_centroid': 'x',
            'y_centroid': 'y',
            'z_centroid': 'z'
        })

        # Альтернатива: использовать центры бинов вместо центроидов
        # result_df = grouped_df[['x_center', 'y_center', 'z_center', 'T']].copy()
        # result_df = result_df.rename(columns={'x_center': 'x', 'y_center': 'y', 'z_center': 'z'})

        print(f"Количество точек после бининга: {len(result_df)}")
        print(f"Степень сжатия: {len(df) / len(result_df):.1f}:1")

        # Дополнительная статистика
        print(f"\nСтатистика бининга:")
        print(f"Диапазон X: [{x_min:.2f}, {x_max:.2f}], ширина бина: {bin_width_x}")
        print(f"Диапазон Y: [{y_min:.2f}, {y_max:.2f}], ширина бина: {bin_width_y}")
        print(f"Диапазон Z: [{z_min:.2f}, {z_max:.2f}], ширина бина: {bin_width_z}")

        return result_df
    

# Пример использования
if __name__ == "__main__":
    loader = DataLoader()
    
    # Загрузка CSV файла
    csv_data = loader.load_from_csv("C:/Users/vkval/Documents/arctica/god0mes1.csv")
    print(f"Загружено {len(csv_data)} записей из CSV")
    print(csv_data.head(5))
    
    # Загрузка DAT файла
    dat_data = loader.load_from_dat("C:/Users/vkval/Documents/arctica/god0mes1.dat")
    print(f"Загружено {len(dat_data)} записей из DAT")
    print(dat_data.head(5))
    
    # Использование универсального метода
    #data = loader.load_data("data.csv")
    #print(f"DataFrame columns: {data.columns.tolist()}")
    #print(f"DataFrame head:\n{data.head()}")