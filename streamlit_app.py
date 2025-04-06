import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import chardet

# Улучшенная функция загрузки данных с автоматическим определением кодировки
@st.cache_data
def load_data(file_name):
    # Определяем кодировку файла
    with open(file_name, 'rb') as f:
        result = chardet.detect(f.read(10000))
    
    # Загружаем данные с определенной кодировкой
    try:
        df = pd.read_csv(file_name, sep=';', encoding=result['encoding'])
    except UnicodeDecodeError:
        # Если автоматическое определение не сработало, пробуем альтернативные кодировки
        try:
            df = pd.read_csv(file_name, sep=';', encoding='utf-8')
        except:
            df = pd.read_csv(file_name, sep=';', encoding='cp1251')
    
    # Очистка данных
    df = df.rename(columns=lambda x: x.strip())  # Удаляем пробелы в названиях столбцов
    if 'Name' in df.columns:
        df['Name'] = df['Name'].str.strip()  # Очищаем названия регионов
    else:
        st.error(f"В файле {file_name} отсутствует столбец 'Name'")
    
    return df

# Загрузка данных с обработкой ошибок
try:
    budget_df = load_data('budget.csv')
    housing_df = load_data('housing.csv')
    investments_df = load_data('investments.csv')
except Exception as e:
    st.error(f"Ошибка загрузки данных: {str(e)}")
    st.stop()

# Заголовок дашборда
st.title('Региональный анализ данных')

# Выбор темы
topic = st.radio(
    "Выберите тему данных:",
    ('Бюджет', 'Жилищный фонд', 'Инвестиции'),
    horizontal=True
)

# Получаем соответствующий датафрейм
if topic == 'Бюджет':
    df = budget_df
    y_label = 'Бюджет (рубли)'
elif topic == 'Жилищный фонд':
    df = housing_df
    y_label = 'Жилищный фонд (кв. м на чел.)'
else:
    df = investments_df
    y_label = 'Инвестиции (рубли)'

# Проверяем, что в данных есть числовые столбцы (годы)
numeric_cols = [col for col in df.columns if str(col).isdigit()]
if not numeric_cols:
    st.error("В данных отсутствуют числовые столбцы (годы). Проверьте формат данных.")
    st.stop()

available_years = [int(col) for col in numeric_cols]
min_year, max_year = min(available_years), max(available_years)

# Выбор диапазона лет
year_range = st.slider(
    'Выберите диапазон лет:',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Фильтрация по годам
year_columns = [str(year) for year in range(year_range[0], year_range[1]+1)]
display_df = df[['Name'] + year_columns]

# Выбор регионов
all_regions = df['Name'].unique()
selected_regions = st.multiselect(
    'Выберите регионы:',
    all_regions,
    default=[all_regions[0]] if len(all_regions) > 0 else []
)

# Проверка выбора регионов
if not selected_regions:
    st.warning("Пожалуйста, выберите хотя бы один регион.")
    st.stop()

# Фильтрация данных по выбранным регионам
filtered_df = display_df[display_df['Name'].isin(selected_regions)]

# Построение графика
st.subheader(f"График данных: {topic}")

fig, ax = plt.subplots(figsize=(12, 6))
colors = list(mcolors.TABLEAU_COLORS.values())

for idx, (_, row) in enumerate(filtered_df.iterrows()):
    region_name = row['Name']
    values = row[year_columns].values
    years = [int(year) for year in year_columns]
    
    ax.plot(
        years,
        values,
        label=region_name,
        color=colors[idx % len(colors)],
        marker='o',
        linewidth=2
    )

ax.set_xlabel('Год', fontsize=12)
ax.set_ylabel(y_label, fontsize=12)
ax.set_title(f'Динамика показателя "{topic}" по выбранным регионам', fontsize=14)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
ax.grid(True, linestyle='--', alpha=0.7)
plt.xticks(years, rotation=45)
plt.tight_layout()

st.pyplot(fig)

# Отображение таблицы с данными
st.subheader("Таблица данных")
st.dataframe(
    filtered_df.reset_index(drop=True),
    height=min(400, len(filtered_df) * 35 + 35),  # Автоподбор высоты таблицы
    use_container_width=True
)

# Дополнительная информация
st.markdown("---")
st.info(f"Данные за период с {year_range[0]} по {year_range[1]} год. Всего регионов: {len(selected_regions)}")
