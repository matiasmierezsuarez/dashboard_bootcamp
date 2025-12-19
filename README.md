<<<<<<< HEAD
# Proyecto Final - Bootcamp de Análisis de Datos 🚀


¡Hola! 👋 Este repositorio contiene el trabajo final desarrollado durante el curso. El objetivo fue simular un entorno real de ingeniería y análisis de datos, construyendo una solución "End-to-End", desde la base de datos hasta la visualización.

## 🏛️ Arquitectura de Datos (Medallion Architecture)


Para garantizar la integridad y calidad de la información, construí una base de datos analítica desde cero aplicando la **Arquitectura Medallón**:


1.  **Bronze Layer (Raw):** Ingesta de los datos crudos tal cual vienen de la fuente.
2.  **Silver Layer (Cleansed):** Procesos de limpieza, normalización y manejo de nulos.
3.  **Gold Layer (Curated):** Modelado dimensional (Fact y Dimensions) listo para ser consumido por herramientas de BI o Dashboards.


## 📊 Visualización (Dashboard con Reflex)


En lugar de usar herramientas tradicionales de BI, opté por desarrollar una aplicación web interactiva utilizando **Python** y el framework **Reflex**. Esto permite una personalización total y demuestra capacidades de desarrollo Full Stack orientado a datos.


### Secciones del Dashboard:

**🏠 Dashboard Principal:**
       **KPIs Clave:** Total de Clientes, Ventas Totales ($) y Cantidad de Órdenes.
       **Segmentación:** Gráficos dinámicos para analizar ventas por Estado, Ciudad y Categoría de producto.
       **Composición:** Gráfico de torta para ver la distribución de ventas.


**📅 Análisis Temporal:**
    Desglose profundo de las ventas a través del tiempo.
    Gráficos de barras y áreas para visualizar tendencias por Año, Mes y Día.
    Filtros interactivos para "drill-down" en fechas específicas.

**💼 Vendedores:**
Ranking (Top 20) de los vendedores con mayor facturación.
Filtro anual para evaluar el rendimiento en diferentes periodos.

To add a new page:
**📋 Tabla de Datos:**
Interfaz para explorar los registros crudos de la capa Gold, con paginación y ordenamiento.


## 🛠️ Stack Tecnológico

**Python:** Lenguaje principal para ETL y Backend.
**Reflex:** Framework para el Frontend y la lógica de la UI.
**PostgreSQL (Neon):** Motor de base de datos en la nube.
**SQL:** Consultas analíticas y transformaciones.
**Asyncpg:** Conector asíncrono de alto rendimiento para la base de datos.

---
*Este proyecto representa la culminación de los conocimientos adquiridos en modelado de datos, SQL y desarrollo de aplicaciones de datos.*
=======
# 📈 Dashboard Analytics - Reflex App

Dashboard interactivo de análisis de ventas construido con Reflex y PostgreSQL (Neon).

## 🚀 Características

- **Métricas Generales**: Total de órdenes, ventas totales, ticket promedio, clientes únicos y vendedores activos
- **Análisis Geográfico**: Estados con más y menos ventas
- **Análisis de Productos**: Producto más vendido y categorías top
- **Top Performers**: Mejor vendedor y mejor cliente
- **Estadísticas Descriptivas**: Media, mediana, moda, desviación estándar, cuartiles (Q1, Q2, Q3), IQR, mínimo y máximo
- **Filtros Dinámicos**: Por fechas, estados, ciudades, categorías y vendedores
- **Análisis en Tiempo Real**: Todos los datos se calculan directamente desde la base de datos

## 📁 Estructura del Proyecto

```
tu_proyecto/
├── config.py           # Configuración de conexión a DB
├── database.py         # Queries y funciones de análisis
├── dashboard.py        # Aplicación principal Reflex
├── requirements.txt    # Dependencias
└── README.md          # Este archivo
```

## 🛠️ Instalación

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 2. Estructura de archivos

Crea los siguientes archivos en tu directorio del proyecto:

- `config.py` - Configuración de la base de datos
- `database.py` - Manager de base de datos y queries
- `dashboard.py` - Aplicación principal (renombra o reemplaza tu archivo existente)


## 📊 Uso del Dashboard

### Filtros de Fecha

1. Selecciona una fecha de inicio y fin
2. Haz clic en "Aplicar" para actualizar todas las métricas

### Análisis Estadístico

1. **Métrica**: Elige entre `total` (precio + flete), `price` (solo precio), o `freight_value` (solo flete)
2. **Agrupar por**: Selecciona cómo filtrar los datos:
   - `customer_state`: Por estado del cliente
   - `seller_state`: Por estado del vendedor
   - `customer_city`: Por ciudad del cliente
   - `product_category_name`: Por categoría de producto
3. **Valor del filtro**: Selecciona un valor específico (ej: un estado o categoría)

Las estadísticas se recalcularán automáticamente mostrando:
- Media, Mediana, Moda
- Desviación Estándar
- Cuartiles (Q1, Q2, Q3) e IQR
- Valores mínimo y máximo
- Total de observaciones

## 🔧 Configuración de la Base de Datos

La conexión a Neon PostgreSQL está configurada en `config.py`. La URL de conexión incluye:

- **Pool size**: 5 conexiones
- **Max overflow**: 10 conexiones adicionales
- **Pool timeout**: 30 segundos
- **Pool recycle**: 3600 segundos (1 hora)

## 📈 Vistas Disponibles

El dashboard utiliza las siguientes vistas de la capa oro:

- `dim_calendar` - Dimensión de fechas
- `dim_customers` - Dimensión de clientes
- `dim_products` - Dimensión de productos
- `dim_sellers` - Dimensión de vendedores
- `dim_status` - Dimensión de estados de órdenes
- `fact_sales` - Tabla de hechos de ventas

## 🎨 Personalización

### Cambiar el tema

En `dashboard.py`, modifica la configuración del tema:

```python
app = rx.App(
    theme=rx.theme(
        appearance="dark",  # "light" o "dark"
        accent_color="blue",  # Cualquier color válido
    )
)
```

### Ajustar límites de resultados

En `database.py`, las funciones aceptan un parámetro `limit`:

```python
db.get_top_states_by_sales(start_date, end_date, limit=20)  # Cambiar a 20 resultados
```

## 🐛 Solución de Problemas

### Error de conexión a la base de datos

- Verifica que la URL en `config.py` sea correcta
- Asegúrate de que tu IP esté permitida en Neon
- Verifica que `psycopg2-binary` esté instalado correctamente


## 📝 Notas Importantes

- Los datos se calculan en **tiempo real** desde la base de datos
- Las estadísticas se recalculan con cada cambio de filtro
- El dashboard está optimizado para grandes volúmenes de datos
- Todas las queries utilizan índices para mejor rendimiento

## 🔄 Próximas Mejoras

- [ ] Exportar datos a CSV/Excel
- [ ] Gráficos interactivos con Plotly
- [ ] Filtros adicionales (por vendedor específico)
- [ ] Comparación de períodos
- [ ] Alertas y notificaciones
- [ ] Dashboard de vendedor individual
>>>>>>> 83c717dee2a017a42a92b8aaa8df21bbab98a084
