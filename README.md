# SAMSUNG-INNOVATION-CAMPUS-PROJECT-1

# Proyecto de Análisis de Datos - Samsung Innovation Campus

Este es un proyecto desarrollado como parte del curso **Samsung Innovation Campus**, con el objetivo de analizar los datos financieros de los estudiantes para proporcionar recomendaciones sobre ingresos, gastos y ahorro.

## Integrantes

- **Aula**: PA09
- **Nombre del equipo**: Newton.py

### Integrantes del equipo:

1. Isaac Delgado
2. Milagros Alonzo
3. Sebastián Rodriguez
4. Carlos Roseman
5. Liseth Abrego

## Introducción

Este proyecto tiene como objetivo analizar los datos financieros de los estudiantes, específicamente su relación entre ingresos y gastos, y su capacidad de ahorro. El análisis se centra en la distribución de los ingresos, las categorías de gastos más comunes y la capacidad de los estudiantes para ahorrar. La herramienta generada tiene una visualización interactiva y un dashboard donde los usuarios pueden explorar estos datos de manera gráfica.

## Herramientas y Librerías

A continuación, se enumeran las herramientas y librerías utilizadas para llevar a cabo el análisis:

### **Librerías utilizadas**:

- **Pandas**: Para la manipulación y análisis de datos (leer archivos CSV/Excel, limpieza de datos, etc.).
- **Matplotlib**: Para la creación de gráficos estáticos (barras, dispersión, pie chart).
- **Streamlit**: Para crear la interfaz de usuario interactiva, incluyendo la visualización de los gráficos y el dashboard.
- **Plotly** (opcional si se desea usar gráficos más avanzados y dinámicos): Para la creación de gráficos interactivos.

### **Otras herramientas**:

- **Jupyter Notebooks** (opcional para exploración de datos previa).
- **VS Code o cualquier IDE de Python** para el desarrollo.

## Estructura del Proyecto

El proyecto está estructurado de la siguiente manera:

student_finance_project/
├── data/
│ ├── raw/ # Datos crudos (dataset.xlsx)
│ ├── interim/ # Datos procesados (dataset_clean.csv)
│ └── processed/ # Datos finales procesados
├── docs/ # Documentación y recursos adicionales
│ └── figures/ # Gráficos generados
├── src/ # Código fuente
│ ├── init.py # Indica que es un paquete
│ ├── config.py # Configuración del proyecto (rutas, etc.)
│ ├── data_prep.py # Preprocesamiento de datos
│ ├── features.py # Generación de gráficos y análisis
│ ├── log.py # Sistema de logging
│ ├── mapping_builder.py # Mapeo de columnas
│ ├── data_audit.py # Auditoría de datos
│ ├── app.py # Streamlit app (landing page + dashboard)
│ └── run_all.py # Orquestador para ejecutar todo el pipeline
├── requirements.txt # Dependencias del proyecto
└── README.md # Este archivo