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