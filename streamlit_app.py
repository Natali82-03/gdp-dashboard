import streamlit as st
import pandas as pd
import plotly.express as px

# Настройка страницы (должна быть первой!)
st.set_page_config(layout="wide", page_title="Анализ жилищного фонда")

@st.cache_data
def load_housing_data():
    try:
        # Загрузка данных с указанием разделителя и десятичного символа
        df = pd.read_csv(
            'housing.csv',
            sep=';',
            encoding='utf-8',
            decimal=',',
            thousands=' '  # Если есть пробелы как разделители тысяч
        )
        
        # Очистка названий регионов (удаление лишних пробелов)
        df['Name'] = df['Name'].str.strip()
        
        # Преобразование годов в целые числа (если нужно)
        df.columns = ['Name'] + [int(col) if str(col).isdigit() else col for col in df.columns[1:]]
        
        return df
    
    except Exception as e:
        st.error(f"Ошибка загрузки данных: {str(e)}")
        return None

# Загрузка данных
housing_df = load_housing_data()
if housing_df is None:
    st.stop()

# Проверка данных (для отладки)
st.write("Первые 5 строк данных:", housing_df.head())

# Доступные годы (из заголовков столбцов)
available_years = [col for col in housing_df.columns if isinstance(col, int)]
min_year, max_year = min(available_years), max(available_years)

# Интерфейс пользователя
st.title("📊 Анализ жилищного фонда Орловской области")

# Сайдбар с настройками
with st.sidebar:
    st.header("⚙️ Настройки отображения")
    
    year_range = st.slider(
        "Диапазон лет:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year)
    )
    
    selected_regions = st.multiselect(
        "Выберите районы/города:",
        options=housing_df['Name'].unique(),
        default=[housing_df['Name'].iloc[0]]  # Первый регион по умолчанию
    )
    
    show_raw_data = st.checkbox("Показать сырые данные", value=False)

# Проверка выбора
if not selected_regions:
    st.warning("Пожалуйста, выберите хотя бы один регион!")
    st.stop()

# Фильтрация данных
filtered_df = housing_df[housing_df['Name'].isin(selected_regions)]

# Преобразование в "длинный" формат для Plotly
melted_df = filtered_df.melt(
    id_vars=['Name'],
    value_vars=[str(y) for y in range(year_range[0], year_range[1]+1)],
    var_name='Year',
    value_name='Площадь (м²/чел)'
)

# Создание графика
fig = px.line(
    melted_df,
    x='Year',
    y='Площадь (м²/чел)',
    color='Name',
    title=f"Динамика жилищного фонда ({year_range[0]}-{year_range[1]})",
    labels={'Name': 'Регион'},
    height=600
)

# Настройка отображения графика
fig.update_layout(
    hovermode='x unified',
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# Отображение графика
st.plotly_chart(fig, use_container_width=True)

# Отображение сырых данных при необходимости
if show_raw_data:
    st.subheader("Исходные данные")
    st.dataframe(filtered_df, use_container_width=True)

# Пояснения
with st.expander("ℹ️ О данных"):
    st.markdown("""
    **Метрики:**
    - Показатель: площадь жилья на человека (м²/чел)
    - Данные за период 2019-2024 гг.
    
    **Инструкция:**
    1. Выберите интересующие регионы
    2. Отрегулируйте диапазон лет
    3. Используйте легенду графика для управления отображением
    """)
