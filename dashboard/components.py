"""
Components - Componentes UI reutilizables
"""
import reflex as rx
import plotly.graph_objects as go
import plotly.express as px


def navbar(state_class) -> rx.Component:
    """Barra de navegación del dashboard"""
    return rx.box(
        rx.hstack(
            rx.heading("📊 Dashboard Analytics", size="6"),
            rx.spacer(),
            rx.hstack(
                nav_button("📈 Overview", "overview", state_class),
                nav_button("📊 Gráficos", "charts", state_class),
                nav_button("🔒 Análisis", "analysis", state_class),
                nav_button("📉 Estadísticas", "statistics", state_class),
                nav_button("📅 Temporal", "temporal", state_class),
                spacing="2",
            ),
            width="100%",
            align="center",
            padding="1em",
        ),
        style={
            "background": "var(--gray-3)",
            "border_bottom": "1px solid var(--gray-6)",
            "position": "sticky",
            "top": "0",
            "z_index": "1000",
        }
    )


def nav_button(label: str, page: str, state_class) -> rx.Component:
    """Botón de navegación"""
    return rx.button(
        label,
        on_click=lambda: state_class.navigate_to(page),
        variant=rx.cond(
            state_class.current_page == page,
            "solid",
            "soft"
        ),
        color_scheme=rx.cond(
            state_class.current_page == page,
            "blue",
            "gray"
        ),
        size="2",
    )


def metric_card(title: str, value: str, subtitle: str = "", icon: str = "📊", color: str = "blue") -> rx.Component:
    """Tarjeta de métrica"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.text(icon, font_size="2.5em"),
                rx.spacer(),
            ),
            rx.text(title, size="2", color="gray", weight="medium"),
            rx.text(value, size="7", weight="bold", color=color),
            rx.cond(
                subtitle != "",
                rx.text(subtitle, size="2", color="gray"),
                rx.fragment()
            ),
            spacing="2",
            align="start",
        ),
        style={"padding": "1.5em", "height": "100%", "background": "var(--gray-2)"}
    )


def global_filters_section(state_class) -> rx.Component:
    """Sección de filtros globales"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.heading("🔍 Filtros Globales", size="5"),
                rx.spacer(),
                rx.cond(
                    state_class.has_active_filters,
                    rx.button(
                        "🗑️ Limpiar Filtros",
                        on_click=state_class.clear_global_filters,
                        size="2",
                        color_scheme="red",
                        variant="soft",
                    ),
                ),
                width="100%",
                align="center",
            ),
            
            rx.divider(),
            
            rx.callout(
                rx.text(state_class.active_filters_text, size="2"),
                icon="filter",
                color_scheme=rx.cond(
                    state_class.has_active_filters,
                    "blue",
                    "gray"
                ),
            ),
            
            rx.grid(
                rx.vstack(
                    rx.text("📅 Fecha Inicio", size="2", weight="bold"),
                    rx.input(
                        type="date",
                        value=state_class.start_date,
                        on_change=state_class.set_start_date,
                        min=state_class.min_available_date,
                        max=state_class.max_available_date,
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("📅 Fecha Fin", size="2", weight="bold"),
                    rx.input(
                        type="date",
                        value=state_class.end_date,
                        on_change=state_class.set_end_date,
                        min=state_class.min_available_date,
                        max=state_class.max_available_date,
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("📍 Estado", size="2", weight="bold"),
                    rx.select(
                        state_class.states_filter_options,
                        placeholder="Todos los estados",
                        value=rx.cond(
                            state_class.selected_state_filter == "",
                            "Todos",
                            state_class.selected_state_filter
                        ),
                        on_change=state_class.set_state_filter,
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                rx.vstack(
                    rx.text("🏷️ Categoría", size="2", weight="bold"),
                    rx.select(
                        state_class.categories_filter_options,
                        placeholder="Todas las categorías",
                        value=rx.cond(
                            state_class.selected_category_filter == "",
                            "Todas",
                            state_class.selected_category_filter
                        ),
                        on_change=state_class.set_category_filter,
                        size="2",
                    ),
                    align="start",
                    spacing="1",
                ),
                columns="4",
                spacing="3",
                width="100%",
            ),
            
            rx.button(
                "✅ Aplicar Filtros",
                on_click=state_class.apply_global_filters,
                size="3",
                color_scheme="blue",
                width="100%",
            ),
            
            spacing="3",
            align="start",
            width="100%",
        ),
        style={"padding": "1.5em", "background": "var(--gray-2)"}
    )


def stats_grid(title: str, stats: dict) -> rx.Component:
    """Grid de estadísticas"""
    return rx.card(
        rx.vstack(
            rx.heading(title, size="5", margin_bottom="0.5em"),
            rx.divider(),
            rx.grid(
                rx.box(
                    rx.vstack(
                        rx.text("Media", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('media', 0):.2f}", size="5", weight="bold", color="blue"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Mediana", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('mediana', 0):.2f}", size="5", weight="bold", color="green"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Moda", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('moda', 0):.2f}", size="5", weight="bold", color="purple"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Desv. Estándar", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('desviacion_std', 0):.2f}", size="5", weight="bold", color="orange"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Q1 (25%)", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('q1', 0):.2f}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Q2 (50%)", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('q2', 0):.2f}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Q3 (75%)", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('q3', 0):.2f}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("IQR", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('iqr', 0):.2f}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Mínimo", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('minimo', 0):.2f}", size="4", weight="bold", color="red"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Máximo", size="2", color="gray", weight="medium"),
                        rx.text(f"${stats.get('maximo', 0):.2f}", size="4", weight="bold", color="green"),
                        spacing="1",
                        align="start"
                    )
                ),
                rx.box(
                    rx.vstack(
                        rx.text("Observaciones", size="2", color="gray", weight="medium"),
                        rx.text(f"{stats.get('count', 0):,}", size="4", weight="bold"),
                        spacing="1",
                        align="start"
                    ),
                    grid_column="span 2"
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),
            spacing="3",
            align="start",
            width="100%",
        ),
        style={"padding": "2em"}
    )


def plotly_chart_card(
    title: str,
    figure: go.Figure,
    loading: bool,
    on_metric_change,
    on_limit_change,
    metric_options: list[str],
    limit_options: list[str],
    selected_metric: str,
    selected_limit: str,
    color: str = "blue"
) -> rx.Component:
    """Card para gráficos Plotly con controles dinámicos"""
    figure = px.line()
    return rx.card(
        rx.vstack(
            rx.heading(title, size="6", color=f"{color}.11"),
            rx.hstack(
                rx.vstack(
                    rx.text("Métrica", size="2", weight="bold"),
                    rx.select(
                        metric_options,
                        value=selected_metric,
                        on_change=on_metric_change,
                        placeholder="Seleccionar métrica",
                        size="2",
                    ),
                    spacing="1",
                    align="start",
                ),
                rx.vstack(
                    rx.text("Top N", size="2", weight="bold"),
                    rx.select(
                        limit_options,
                        value=selected_limit,
                        on_change=on_limit_change,
                        placeholder="Cantidad",
                        size="2",
                    ),
                    spacing="1",
                    align="start",
                ),
                spacing="4",
                width="100%",
            ),
            rx.divider(),
            rx.cond(
                loading,
                rx.center(
                    rx.vstack(
                        rx.spinner(size="3"),
                        rx.text("Cargando datos...", size="2"),
                        spacing="2",
                    ),
                    height="500px",
                ),
                rx.plotly(data=figure, layout={"responsive": True})
            ),
            spacing="4",
            width="100%",
        ),
        width="100%",
        style={"padding": "2em"}
    )