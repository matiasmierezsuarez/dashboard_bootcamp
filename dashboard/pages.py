"""
Pages - Páginas del dashboard
"""
import reflex as rx
from .components import metric_card, stats_grid, plotly_chart_card


def overview_metrics(state_class) -> rx.Component:
    """Métricas generales en tarjetas"""
    return rx.grid(
        metric_card(
            "Total Órdenes",
            f"{state_class.overview_metrics.get('total_ordenes', 0):,.0f}",
            "Órdenes procesadas",
            "🛒",
            "blue"
        ),
        metric_card(
            "Ventas Totales",
            f"${state_class.overview_metrics.get('ventas_totales', 0):,.2f}",
            "Ingresos generados",
            "💰",
            "green"
        ),
        metric_card(
            "Ticket Promedio",
            f"${state_class.overview_metrics.get('ticket_promedio', 0):,.2f}",
            "Valor por orden",
            "🎫",
            "purple"
        ),
        metric_card(
            "Clientes Únicos",
            f"{state_class.overview_metrics.get('clientes_unicos', 0):,.0f}",
            "Clientes activos",
            "👥",
            "orange"
        ),
        metric_card(
            "Vendedores Activos",
            f"{state_class.overview_metrics.get('vendedores_activos', 0):,.0f}",
            "En el período",
            "🪙",
            "red"
        ),
        columns="5",
        spacing="4",
        width="100%",
    )


def top_performers(state_class) -> rx.Component:
    """Top vendedor, cliente y producto"""
    return rx.grid(
        # Top Vendedor
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("🏆", font_size="2em"),
                    rx.heading("Mejor Vendedor", size="4"),
                    spacing="2",
                ),
                rx.divider(),
                rx.cond(
                    state_class.top_seller_data != {},
                    rx.vstack(
                        rx.text(
                            state_class.seller_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            f"📍 {state_class.top_seller_data.get('seller_city', '')}, {state_class.top_seller_data.get('seller_state', '')}",
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Ventas:", size="2", color="gray"),
                                rx.text(
                                    f"${state_class.top_seller_data.get('ventas_totales', 0):,.2f}",
                                    weight="bold",
                                    size="4",
                                    color="green"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Órdenes:", size="2", color="gray"),
                                rx.text(
                                    f"{state_class.top_seller_data.get('total_ordenes', 0):,.0f}",
                                    weight="bold",
                                    size="4"
                                ),
                                spacing="2",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    rx.text("Sin datos", color="gray")
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            style={"padding": "1.5em", "height": "100%"}
        ),
        # Top Cliente
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("🌟", font_size="2em"),
                    rx.heading("Mejor Cliente", size="4"),
                    spacing="2",
                ),
                rx.divider(),
                rx.cond(
                    state_class.top_customer_data != {},
                    rx.vstack(
                        rx.text(
                            state_class.customer_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            f"📍 {state_class.top_customer_data.get('customer_city', '')}, {state_class.top_customer_data.get('customer_state', '')}",
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Compras:", size="2", color="gray"),
                                rx.text(
                                    f"${state_class.top_customer_data.get('total_comprado', 0):,.2f}",
                                    weight="bold",
                                    size="4",
                                    color="green"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Órdenes:", size="2", color="gray"),
                                rx.text(
                                    f"{state_class.top_customer_data.get('total_ordenes', 0):,.0f}",
                                    weight="bold",
                                    size="4"
                                ),
                                spacing="2",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    rx.text("Sin datos", color="gray")
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            style={"padding": "1.5em", "height": "100%"}
        ),
        # Top Producto
        rx.card(
            rx.vstack(
                rx.hstack(
                    rx.text("🥇", font_size="2em"),
                    rx.heading("Producto Más Vendido", size="4"),
                    spacing="2",
                ),
                rx.divider(),
                rx.cond(
                    state_class.top_product_data != {},
                    rx.vstack(
                        rx.text(
                            state_class.product_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            state_class.top_product_data.get('categoria', 'N/A'),
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Unidades:", size="2", color="gray"),
                                rx.text(
                                    f"{state_class.top_product_data.get('unidades_vendidas', 0):,.0f}",
                                    weight="bold",
                                    size="4",
                                    color="white"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Ventas:", size="2", color="gray"),
                                rx.text(
                                    f"${state_class.top_product_data.get('ventas_totales', 0):,.2f}",
                                    weight="bold",
                                    size="4",
                                    color="green"
                                ),
                                spacing="2",
                            ),
                            spacing="1",
                            align="start",
                            width="100%",
                        ),
                        spacing="2",
                        align="start",
                        width="100%",
                    ),
                    rx.text("Sin datos", color="gray")
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            style={"padding": "1.5em", "height": "100%"}
        ),
        columns="3",
        spacing="4",
    )


def overview_page(state_class) -> rx.Component:
    """Página Overview"""
    return rx.vstack(
        rx.heading("📈 Vista General", size="7"),
        overview_metrics(state_class),
        top_performers(state_class),
        spacing="5",
        width="100%",
    )


def charts_page(state_class) -> rx.Component:
    """Página de Gráficos Plotly"""
    return rx.vstack(
        rx.card(
            rx.hstack(
                rx.heading("📊 Gráficos Interactivos Dinámicos", size="6"),
                rx.spacer(),
                rx.button(
                    "🔄 Cargar Todos los Gráficos",
                    on_click=state_class.load_all_plotly_charts,
                    size="3",
                    color_scheme="blue",
                ),
                width="100%",
                align="center",
            ),
            style={"padding": "1.5em", "background": "var(--gray-2)"}
        ),
        rx.callout(
            rx.text("💡 Usa los selectores para cambiar la métrica y la cantidad de resultados mostrados"),
            icon="info",
            color="white",
        ),
        rx.grid(
            plotly_chart_card(
                title="📍 Ventas por Estado",
                figure=state_class.fig_states_plotly,
                loading=state_class.loading_chart_states,
                on_metric_change=state_class.update_metric_state,
                on_limit_change=state_class.update_limit_state,
                metric_options=state_class.metric_options,
                limit_options=state_class.limit_options,
                selected_metric=state_class.selected_metric_state,
                selected_limit=state_class.num_states_to_show,
                color="blue",
            ),
            plotly_chart_card(
                title="🏙️ Ventas por Ciudad",
                figure=state_class.fig_cities_plotly,
                loading=state_class.loading_chart_cities,
                on_metric_change=state_class.update_metric_city,
                on_limit_change=state_class.update_limit_city,
                metric_options=state_class.metric_options,
                limit_options=state_class.limit_options,
                selected_metric=state_class.selected_metric_city,
                selected_limit=state_class.num_cities_to_show,
                color="green",
            ),
            plotly_chart_card(
                title="🏷️ Ventas por Categoría",
                figure=state_class.fig_categories_plotly,
                loading=state_class.loading_chart_categories,
                on_metric_change=state_class.update_metric_category,
                on_limit_change=state_class.update_limit_category,
                metric_options=state_class.metric_options,
                limit_options=state_class.limit_options,
                selected_metric=state_class.selected_metric_category,
                selected_limit=state_class.num_categories_to_show,
                color="purple",
            ),
            plotly_chart_card(
                title="🪙 Ventas por Vendedor",
                figure=state_class.fig_sellers_plotly,
                loading=state_class.loading_chart_sellers,
                on_metric_change=state_class.update_metric_seller,
                on_limit_change=state_class.update_limit_seller,
                metric_options=state_class.metric_options,
                limit_options=state_class.limit_options,
                selected_metric=state_class.selected_metric_seller,
                selected_limit=state_class.num_sellers_to_show,
                color="orange",
            ),
            columns="1",
            spacing="5",
            width="100%",
        ),
        spacing="4",
        width="100%",
    )


def analysis_page(state_class) -> rx.Component:
    """Página de Análisis (Gráficos Recharts)"""
    return rx.vstack(
        rx.heading("📑 Análisis por Dimensión", size="9"),
        rx.card(
            rx.vstack(
                rx.heading("📊 Top 10 Estados por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    state_class.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#8884d8",
                        ),
                        rx.recharts.x_axis(data_key="estado"),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=state_class.top_states_chart,
                        width="100%",
                        height=400,
                    ),
                    rx.center(
                        rx.text("No hay datos disponibles", color="gray", size="4"),
                        padding="4em"
                    )
                ),
                spacing="3",
                width="100%",
            ), width="100%",
            style={"padding": "2em"}
        ),
        rx.card(
            rx.vstack(
                rx.heading("🏷️ Top 10 Categorías por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    state_class.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#82ca9d",
                        ),
                        rx.recharts.x_axis(
                            data_key="categoria", 
                            angle=-45, 
                            text_anchor="end", 
                            height=100
                        ),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=state_class.categories_chart,
                        width="100%",
                        height=450,
                    ),
                    rx.center(
                        rx.text("No hay datos disponibles", color="gray", size="4"),
                        padding="4em"
                    )
                ),
                spacing="3",
                width="100%",
            ), width="100%",
            style={"padding": "2em"}
        ),
        rx.card(
            rx.vstack(
                rx.heading("📉 Bottom 10 Estados por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    state_class.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#ff7c7c",
                        ),
                        rx.recharts.x_axis(data_key="estado"),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=state_class.bottom_states_chart,
                        width="100%",
                        height=400,
                    ),
                    rx.center(
                        rx.text("No hay datos disponibles", color="gray", size="4"),
                        padding="4em"
                    )
                ),
                spacing="3",
                width="100%",
            ), width="100%",
            style={"padding": "2em"}
        ),
        spacing="4",
        width="100%",
    )


def statistics_page(state_class) -> rx.Component:
    """Página de Estadísticas"""
    return rx.vstack(
        rx.heading("📉 Análisis Estadístico", size="7"),
        rx.card(
            rx.vstack(
                rx.heading("🔧 Configuración de Análisis", size="5", color="gray"),
                rx.grid(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            ["total", "price", "freight_value"],
                            value=state_class.selected_metric,
                            on_change=state_class.set_metric,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Agrupar por", size="2", weight="bold"),
                        rx.select(
                            ["customer_state", "seller_state", "customer_city", "product_category_name"],
                            value=state_class.selected_group,
                            on_change=state_class.set_group,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    columns="2",
                    spacing="3",
                    width="100%",
                ),
                rx.cond(
                    state_class.selected_group == "customer_state",
                    rx.vstack(
                        rx.text("Filtrar Estado", size="2", weight="bold"),
                        rx.select(
                            state_class.states_options,
                            placeholder="Selecciona un estado",
                            value=rx.cond(
                                state_class.selected_filter_value == "",
                                "Todos",
                                state_class.selected_filter_value
                            ),
                            on_change=state_class.set_filter_value,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        width="100%",
                    ),
                ),
                rx.cond(
                    state_class.selected_group == "product_category_name",
                    rx.vstack(
                        rx.text("Filtrar Categoría", size="2", weight="bold"),
                        rx.select(
                            state_class.categories_options,
                            placeholder="Selecciona una categoría",
                            value=rx.cond(
                                state_class.selected_filter_value == "",
                                "Todas",
                                state_class.selected_filter_value
                            ),
                            on_change=state_class.set_filter_value,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        width="100%",
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            style={"padding": "1.5em", "background": "var(--gray-2)"}
        ),
        stats_grid("📊 Análisis Estadístico Descriptivo", state_class.statistics_data),
        spacing="4",
        width="100%",
    )


def temporal_analysis_page(state_class) -> rx.Component:
    """Página de Análisis Temporal"""
    return rx.vstack(
        rx.card(
            rx.hstack(
                rx.heading("📅 Análisis Temporal de Ventas", size="6"),
                rx.spacer(),
                rx.button(
                    "🔄 Cargar Todos los Gráficos",
                    on_click=state_class.load_all_temporal_charts,
                    size="3",
                    color_scheme="blue",
                ),
                width="100%",
                align="center",
            ), width="100%",
            style={"padding": "1.5em", "background": "var(--gray-2)"}
        ),
        
        rx.callout(
            rx.text("📊 Visualiza las tendencias de ventas a lo largo del tiempo. Los filtros globales de estado y categoría se aplican a todos los gráficos."),
            icon="info",
            color_scheme="blue",
        ),
        
        # Gráfico por Año
        rx.card(
            rx.vstack(
                rx.heading("📈 Ventas por Año", size="5", color="blue.11"),
                rx.hstack(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            state_class.temporal_metric_options,
                            value=state_class.selected_metric_year,
                            on_change=state_class.update_metric_year,
                            placeholder="Seleccionar métrica",
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
                    state_class.loading_chart_year,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando datos...", size="2"),
                            spacing="2",
                        ),
                        height="500px",
                    ),
                    rx.cond(
                        state_class.has_year_data,
                        rx.plotly(
                            data=state_class.fig_sales_by_year,
                            layout={"responsive": True}
                        ),
                        rx.center(
                            rx.text("No hay datos disponibles. Haz clic en 'Cargar Todos los Gráficos'", 
                                   color="gray", size="3"),
                            height="500px",
                        )
                    )
                ),
                spacing="4",
                width="100%",
            ), width="100%",
            style={"padding": "2em"}
        ),
        
        # Gráfico por Año-Mes
        rx.card(
            rx.vstack(
                rx.heading("📊 Ventas por Año-Mes", size="5", color="green.11"),
                rx.hstack(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            state_class.temporal_metric_options,
                            value=state_class.selected_metric_year_month,
                            on_change=state_class.update_metric_year_month,
                            placeholder="Seleccionar métrica",
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("📅 Fecha Inicio", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=state_class.start_date_month,
                            on_change=state_class.set_start_date_month,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("📅 Fecha Fin", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=state_class.end_date_month,
                            on_change=state_class.set_end_date_month,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.button(
                        "✅ Aplicar Fechas",
                        on_click=state_class.apply_month_filters,
                        size="2",
                        color_scheme="blue",
                    ),
                    spacing="4",
                    width="100%",
                    align="end",
                ),
                rx.divider(),
                rx.cond(
                    state_class.loading_chart_year_month,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando datos...", size="2"),
                            spacing="2",
                        ),
                        height="500px",
                    ),
                    rx.cond(
                        state_class.has_year_month_data,
                        rx.plotly(
                            data=state_class.fig_sales_by_year_month,
                            layout={"responsive": True}
                        ),
                        rx.center(
                            rx.text("No hay datos disponibles. Selecciona un rango de fechas y haz clic en 'Aplicar Fechas'", 
                                   color="gray", size="3"),
                            height="500px",
                        )
                    )
                ),
                spacing="4",
                width="100%",
            ), width="100%",
            style={"padding": "2em"}
        ),
        
        # Gráfico por Año-Mes-Día
        rx.card(
            rx.vstack(
                rx.heading("📉 Ventas por Año-Mes-Día", size="5", color="purple.11"),
                rx.hstack(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            state_class.temporal_metric_options,
                            value=state_class.selected_metric_year_month_day,
                            on_change=state_class.update_metric_year_month_day,
                            placeholder="Seleccionar métrica",
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("📅 Fecha Inicio", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=state_class.start_date_day,
                            on_change=state_class.set_start_date_day,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.vstack(
                        rx.text("📅 Fecha Fin", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=state_class.end_date_day,
                            on_change=state_class.set_end_date_day,
                            size="2",
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.button(
                        "✅ Aplicar Fechas",
                        on_click=state_class.apply_day_filters,
                        size="2",
                        color_scheme="blue",
                    ),
                    spacing="4",
                    width="100%",
                    align="end",
                ),
                rx.callout(
                    rx.text("Recomendación: Usa rangos de fechas cortos (1-3 meses) para mejor visualización de datos diarios"),
                    icon="triangle_alert",
                    color_scheme="orange",
                    size="1",
                ),
                rx.divider(),
                rx.cond(
                    state_class.loading_chart_year_month_day,
                    rx.center(
                        rx.vstack(
                            rx.spinner(size="3"),
                            rx.text("Cargando datos...", size="2"),
                            spacing="2",
                        ),
                        height="500px",
                    ),
                    rx.cond(
                        state_class.has_year_month_day_data,
                        rx.plotly(
                            data=state_class.fig_sales_by_year_month_day,
                            layout={"responsive": True}
                        ),
                        rx.center(
                            rx.text("No hay datos disponibles. Selecciona un rango de fechas y haz clic en 'Aplicar Fechas'", 
                                   color="gray", size="3"),
                            height="500px",
                        )
                    )
                ),
                spacing="4",
                width="100%",
            ), width="100%",
            style={"padding": "2em"}
        ),
        
        spacing="4",
        width="100%",
    )