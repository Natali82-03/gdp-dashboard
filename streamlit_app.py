import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Load data functions
@st.cache_data
def load_data(file_name):
    df = pd.read_csv(file_name, sep=';', encoding='utf-8')
    df = df.rename(columns=lambda x: x.strip())  # Clean column names
    df['Name'] = df['Name'].str.strip()  # Clean region names
    return df

# Load all datasets
budget_df = load_data('budget.csv')
housing_df = load_data('housing.csv')
investments_df = load_data('investments.csv')

# Dashboard title
st.title('Региональный анализ данных')

# Topic selection
topic = st.radio(
    "Выберите тему данных:",
    ('Бюджет', 'Жилищный фонд', 'Инвестиции'),
    horizontal=True
)

# Get appropriate dataframe
if topic == 'Бюджет':
    df = budget_df
    y_label = 'Бюджет (рубли)'
elif topic == 'Жилищный фонд':
    df = housing_df
    y_label = 'Жилищный фонд (кв. м на чел.)'
else:
    df = investments_df
    y_label = 'Инвестиции (рубли)'

# Year range selection
available_years = [int(col) for col in df.columns if col.isdigit()]
min_year, max_year = min(available_years), max(available_years)

year_range = st.slider(
    'Выберите диапазон лет:',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filter years
year_columns = [str(year) for year in range(year_range[0], year_range[1]+1)]
display_df = df[['Name'] + year_columns]

# Region selection
all_regions = df['Name'].unique()
selected_regions = st.multiselect(
    'Выберите регионы:',
    all_regions,
    default=all_regions[0]  # Default to first region
)

# Filter data for selected regions
filtered_df = display_df[display_df['Name'].isin(selected_regions)]

# Plotting
if not selected_regions:
    st.warning("Пожалуйста, выберите хотя бы один регион.")
else:
    st.subheader(f"График данных: {topic}")
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Get distinct colors for each region
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
            marker='o'
        )
    
    ax.set_xlabel('Год')
    ax.set_ylabel(y_label)
    ax.set_title(f'Динамика показателя "{topic}" по выбранным регионам')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(True)
    
    # Rotate x-axis labels for better readability
    plt.xticks(years, rotation=45)
    
    st.pyplot(fig)
    
    # Show data table
    st.subheader("Таблица данных")
    st.dataframe(filtered_df.reset_index(drop=True))
