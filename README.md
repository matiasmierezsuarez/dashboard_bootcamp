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
proyecto_final/
├── __init__.py
├── database.py          
├── state.py            
├── events.py           
├── components.py       
├── pages.py            
└── dashboard.py        
```
📝 Guía de Modificación
Para agregar una nueva página:

En pages.py - Agregar la función de la página:

pythondef nueva_pagina(state_class) -> rx.Component:
    return rx.vstack(
        rx.heading("Mi Nueva Página"),
        # ... tu contenido
    )

En components.py - Agregar botón en navbar:

pythonnav_button("🆕 Nueva", "nueva", state_class),

En dashboard.py - Importar y agregar condición:

pythonfrom .pages import ..., nueva_pagina

# En index():
rx.cond(
    DashboardState.current_page == "nueva",
    nueva_pagina(DashboardState),
),
Para agregar nuevos eventos:

En events.py - Agregar método estático:

pythonclass MiNuevaClase:
    @staticmethod
    def mi_evento(state, param):
        # lógica del evento
        pass

En dashboard.py - Vincular al estado:

pythonDashboardState.mi_evento = rx.event(MiNuevaClase.mi_evento)
Para agregar componentes reutilizables:
En components.py:
pythondef mi_componente(titulo: str, datos: dict) -> rx.Component:
    return rx.card(
        # ... tu componente
    )
Luego úsalo en cualquier página importándolo:
pythonfrom .components import mi_componente
🔍 Arquitectura del Sistema
┌─────────────────────────────────────────┐
│           dashboard.py                  │
│     (Punto de entrada principal)        │
│  - Configura la app                     │
│  - Vincula eventos al estado            │
│  - Define la página index()             │
└────────────┬────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌──────────┐
│ state.py│◄─────┤events.py │
│ (Estado)│      │ (Lógica) │
└────┬────┘      └──────────┘
     │
     ▼
┌──────────────┐      ┌──────────┐
│components.py │◄─────┤pages.py  │
│ (UI Base)    │      │(Páginas) │
└──────────────┘      └──────────┘
⚠️ Notas Importantes

No modifiques database.py - mantiene la misma funcionalidad
El archivo principal ahora solo orquesta, no implementa lógica
Los eventos se vinculan dinámicamente al estado en dashboard.py
Las páginas reciben state_class como parámetro para acceder al estado

🧪 Testing
Para verificar que todo funciona:

Ejecuta la aplicación:

bashreflex run

Verifica que cada página se carga correctamente
Prueba los filtros globales
Verifica los gráficos interactivos
Comprueba el análisis temporal

🐛 Solución de Problemas Comunes
Error: "module has no attribute..."

Verifica que los imports estén correctos en dashboard.py
Asegúrate de haber creado todos los archivos

Error: "State method not found"

Verifica que el evento esté vinculado en dashboard.py
Revisa que el decorador @rx.event esté presente donde corresponda

Los gráficos no se cargan

Verifica que database.py no haya sido modificado
Comprueba que las importaciones de pandas y plotly estén presentes