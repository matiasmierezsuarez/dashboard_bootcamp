"""Welcome to Reflex! This file outlines the steps to create a basic app."""
"""
Dashboard Analytics - Aplicación con Gráficos Interactivos
"""
import reflex as rx
from datetime import datetime, timedelta
from .database import db
import pandas as pd


class DashboardState(rx.State):
    """Estado principal del dashboard"""
    
    # Filtros de fecha
    start_date: str = ""
    end_date: str = ""
    min_available_date: str = ""
    max_available_date: str = ""
    
    # Filtros adicionales
    selected_metric: str = "total"
    selected_group: str = "customer_state"
    selected_filter_value: str = ""
    
    # Datos para gráficos (formato para Recharts)
    top_states_chart: list[dict] = []
    bottom_states_chart: list[dict] = []
    categories_chart: list[dict] = []
    
    # Datos para métricas
    top_product_data: dict = {}
    top_seller_data: dict = {}
    top_customer_data: dict = {}
    overview_metrics: dict = {}
    statistics_data: dict = {}
    
    # Opciones para filtros
    available_states: list[str] = []
    available_categories: list[str] = []
    
    # Estado de carga
    is_loading: bool = False
    
    # Computed vars
    @rx.var
    def states_options(self) -> list[str]:
        return ["Todos"] + self.available_states
    
    @rx.var
    def categories_options(self) -> list[str]:
        return ["Todas"] + self.available_categories
    
    @rx.var
    def has_data(self) -> bool:
        return len(self.top_states_chart) > 0
    
    # Computed vars para textos truncados
    @rx.var
    def seller_id_display(self) -> str:
        seller_id = self.top_seller_data.get('seller_id', 'N/A')
        return seller_id[:20] if len(seller_id) > 20 else seller_id
    
    @rx.var
    def customer_id_display(self) -> str:
        customer_id = self.top_customer_data.get('customer_id', 'N/A')
        return customer_id[:20] if len(customer_id) > 20 else customer_id
    
    @rx.var
    def product_id_display(self) -> str:
        product_id = self.top_product_data.get('product_id', 'N/A')
        return product_id[:20] if len(product_id) > 20 else product_id
    
    def on_mount(self):
        """Se ejecuta al cargar la página"""
        self.load_initial_data()
    
    def load_initial_data(self):
        """Carga datos iniciales"""
        self.is_loading = True
        
        # Obtener rango de fechas
        min_date, max_date = db.get_date_range()
        self.min_available_date = min_date
        self.max_available_date = max_date
        
        # Últimos 6 meses
        end = datetime.strptime(max_date, "%Y-%m-%d")
        start = end - timedelta(days=180)
        self.start_date = start.strftime("%Y-%m-%d")
        self.end_date = max_date
        
        # Cargar opciones
        self.available_states = db.get_available_states()
        self.available_categories = db.get_available_categories()
        
        # Cargar datos
        self.refresh_data()
        self.is_loading = False
    
    def refresh_data(self):
        """Actualiza todos los datos del dashboard"""
        self.is_loading = True
        
        # Métricas generales
        self.overview_metrics = db.get_overview_metrics(
            self.start_date if self.start_date else None,
            self.end_date if self.end_date else None
        )
        
        # Top Estados - preparar para gráfico
        df_top = db.get_top_states_by_sales(self.start_date, self.end_date, 10)
        if not df_top.empty:
            self.top_states_chart = [
                {
                    "estado": row["estado"],
                    "ventas": float(row["ventas_totales"]),
                    "ordenes": int(row["total_ordenes"])
                }
                for _, row in df_top.iterrows()
            ]
        
        # Bottom Estados
        df_bottom = db.get_bottom_states_by_sales(self.start_date, self.end_date, 10)
        if not df_bottom.empty:
            self.bottom_states_chart = [
                {
                    "estado": row["estado"],
                    "ventas": float(row["ventas_totales"]),
                    "ordenes": int(row["total_ordenes"])
                }
                for _, row in df_bottom.iterrows()
            ]
        
        # Categorías - preparar para gráfico
        df_categories = db.get_top_categories(self.start_date, self.end_date, 10)
        if not df_categories.empty:
            self.categories_chart = [
                {
                    "categoria": row["categoria"][:20],  # Truncar nombres largos
                    "ventas": float(row["ventas_totales"]),
                    "unidades": int(row["unidades_vendidas"])
                }
                for _, row in df_categories.iterrows()
            ]
        
        # Top producto
        df_product = db.get_top_product(self.start_date, self.end_date)
        self.top_product_data = df_product.iloc[0].to_dict() if not df_product.empty else {}
        
        # Top vendedor
        df_seller = db.get_top_seller(self.start_date, self.end_date)
        self.top_seller_data = df_seller.iloc[0].to_dict() if not df_seller.empty else {}
        
        # Top cliente
        df_customer = db.get_top_customer(self.start_date, self.end_date)
        self.top_customer_data = df_customer.iloc[0].to_dict() if not df_customer.empty else {}
        
        # Estadísticas
        self.calculate_statistics()
        self.is_loading = False
    
    def calculate_statistics(self):
        """Calcula estadísticas"""
        self.statistics_data = db.get_statistics(
            metric=self.selected_metric,
            group_by=self.selected_group if self.selected_filter_value else None,
            filter_value=self.selected_filter_value if self.selected_filter_value else None,
            start_date=self.start_date if self.start_date else None,
            end_date=self.end_date if self.end_date else None
        )
    
    def set_start_date(self, value: str):
        self.start_date = value
    
    def set_end_date(self, value: str):
        self.end_date = value
    
    def apply_date_filter(self):
        self.refresh_data()
    
    def set_metric(self, value: str):
        self.selected_metric = value
        self.calculate_statistics()
    
    def set_group(self, value: str):
        self.selected_group = value
        self.selected_filter_value = ""
    
    def set_filter_value(self, value: str):
        if value in ["Todos", "Todas"]:
            self.selected_filter_value = ""
        else:
            self.selected_filter_value = value
        self.calculate_statistics()


# ==================== COMPONENTES UI ====================

def metric_card(title: str, value: str, subtitle: str = "", icon: str = "📊", color: str = "blue") -> rx.Component:
    """Tarjeta de métrica con color"""
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


def stats_grid(title: str, stats: dict) -> rx.Component:
    """Grid de estadísticas"""
    return rx.card(
        rx.vstack(
            rx.heading(title, size="5", margin_bottom="0.5em"),
            rx.divider(),
            rx.grid(
                # Fila 1: Tendencia central
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
                # Fila 2: Cuartiles
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
                # Fila 3: Extremos
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


def filter_section() -> rx.Component:
    """Sección de filtros mejorada"""
    return rx.card(
        rx.vstack(
            rx.heading("🔍 Filtros y Configuración", size="5"),
            rx.divider(),
            
            # Filtros de fecha
            rx.vstack(
                rx.heading("📅 Rango de Fechas", size="3", color="gray"),
                rx.hstack(
                    rx.vstack(
                        rx.text("Desde", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=DashboardState.start_date,
                            on_change=DashboardState.set_start_date,
                            min=DashboardState.min_available_date,
                            max=DashboardState.max_available_date,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        flex="1",
                    ),
                    rx.vstack(
                        rx.text("Hasta", size="2", weight="bold"),
                        rx.input(
                            type="date",
                            value=DashboardState.end_date,
                            on_change=DashboardState.set_end_date,
                            min=DashboardState.min_available_date,
                            max=DashboardState.max_available_date,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        flex="1",
                    ),
                    rx.button(
                        "Aplicar",
                        on_click=DashboardState.apply_date_filter,
                        size="3",
                        style={"margin_top": "1.8em"},
                        color_scheme="blue",
                    ),
                    spacing="3",
                    width="100%",
                ),
                spacing="2",
                width="100%",
            ),
            
            rx.divider(),
            
            # Filtros estadísticos
            rx.vstack(
                rx.heading("📊 Análisis Estadístico", size="3", color="gray"),
                rx.grid(
                    rx.vstack(
                        rx.text("Métrica", size="2", weight="bold"),
                        rx.select(
                            ["total", "price", "freight_value"],
                            value=DashboardState.selected_metric,
                            on_change=DashboardState.set_metric,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                    ),
                    rx.vstack(
                        rx.text("Agrupar por", size="2", weight="bold"),
                        rx.select(
                            ["customer_state", "seller_state", "customer_city", "product_category_name"],
                            value=DashboardState.selected_group,
                            on_change=DashboardState.set_group,
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
                    DashboardState.selected_group == "customer_state",
                    rx.vstack(
                        rx.text("Filtrar Estado", size="2", weight="bold"),
                        rx.select(
                            DashboardState.states_options,
                            placeholder="Selecciona un estado",
                            value=rx.cond(
                                DashboardState.selected_filter_value == "",
                                "Todos",
                                DashboardState.selected_filter_value
                            ),
                            on_change=DashboardState.set_filter_value,
                            size="3",
                        ),
                        align="start",
                        spacing="1",
                        width="100%",
                    ),
                ),
                rx.cond(
                    DashboardState.selected_group == "product_category_name",
                    rx.vstack(
                        rx.text("Filtrar Categoría", size="2", weight="bold"),
                        rx.select(
                            DashboardState.categories_options,
                            placeholder="Selecciona una categoría",
                            value=rx.cond(
                                DashboardState.selected_filter_value == "",
                                "Todas",
                                DashboardState.selected_filter_value
                            ),
                            on_change=DashboardState.set_filter_value,
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
            
            spacing="4",
            align="start",
            width="100%",
        ),
        style={"padding": "1.5em", "background": "var(--gray-2)"}
    )


def overview_metrics() -> rx.Component:
    """Métricas generales en tarjetas"""
    return rx.grid(
        metric_card(
            "Total Órdenes",
            f"{DashboardState.overview_metrics.get('total_ordenes', 0):,.0f}",
            "Órdenes procesadas",
            "🛍️",
            "blue"
        ),
        metric_card(
            "Ventas Totales",
            f"${DashboardState.overview_metrics.get('ventas_totales', 0):,.2f}",
            "Ingresos generados",
            "💰",
            "green"
        ),
        metric_card(
            "Ticket Promedio",
            f"${DashboardState.overview_metrics.get('ticket_promedio', 0):,.2f}",
            "Valor por orden",
            "🎫",
            "purple"
        ),
        metric_card(
            "Clientes Únicos",
            f"{DashboardState.overview_metrics.get('clientes_unicos', 0):,.0f}",
            "Clientes activos",
            "👥",
            "orange"
        ),
        metric_card(
            "Vendedores Activos",
            f"{DashboardState.overview_metrics.get('vendedores_activos', 0):,.0f}",
            "En el período",
            "🏪",
            "red"
        ),
        columns="5",
        spacing="4",
        width="100%",
    )


def top_performers() -> rx.Component:
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
                    DashboardState.top_seller_data != {},
                    rx.vstack(
                        rx.text(
                            DashboardState.seller_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            f"📍 {DashboardState.top_seller_data.get('seller_city', '')}, {DashboardState.top_seller_data.get('seller_state', '')}",
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Ventas:", size="2", color="gray"),
                                rx.text(
                                    f"${DashboardState.top_seller_data.get('ventas_totales', 0):,.2f}",
                                    weight="bold",
                                    size="4",
                                    color="green"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Órdenes:", size="2", color="gray"),
                                rx.text(
                                    f"{DashboardState.top_seller_data.get('total_ordenes', 0):,.0f}",
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
                    DashboardState.top_customer_data != {},
                    rx.vstack(
                        rx.text(
                            DashboardState.customer_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            f"📍 {DashboardState.top_customer_data.get('customer_city', '')}, {DashboardState.top_customer_data.get('customer_state', '')}",
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Compras:", size="2", color="gray"),
                                rx.text(
                                    f"${DashboardState.top_customer_data.get('total_comprado', 0):,.2f}",
                                    weight="bold",
                                    size="4",
                                    color="green"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Órdenes:", size="2", color="gray"),
                                rx.text(
                                    f"{DashboardState.top_customer_data.get('total_ordenes', 0):,.0f}",
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
                    DashboardState.top_product_data != {},
                    rx.vstack(
                        rx.text(
                            DashboardState.product_id_display,
                            weight="bold",
                            size="5"
                        ),
                        rx.text(
                            DashboardState.top_product_data.get('categoria', 'N/A'),
                            color="gray",
                            size="2"
                        ),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Unidades:", size="2", color="gray"),
                                rx.text(
                                    f"{DashboardState.top_product_data.get('unidades_vendidas', 0):,.0f}",
                                    weight="bold",
                                    size="4",
                                    color="blue"
                                ),
                                spacing="2",
                            ),
                            rx.hstack(
                                rx.text("Ventas:", size="2", color="gray"),
                                rx.text(
                                    f"${DashboardState.top_product_data.get('ventas_totales', 0):,.2f}",
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


def charts_section() -> rx.Component:
    """Sección de gráficos completa"""
    return rx.vstack(
        # 1. Gráfico: Top Estados (El que ya funciona)
        rx.card(
            rx.vstack(
                rx.heading("📊 Top 10 Estados por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    DashboardState.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#8884d8",
                        ),
                        rx.recharts.x_axis(data_key="estado"),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=DashboardState.top_states_chart,
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
            ),
            style={"padding": "2em"}
        ),
        
        # 2. Gráfico: Categorías
        rx.card(
            rx.vstack(
                rx.heading("🏷️ Top 10 Categorías por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    DashboardState.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#82ca9d",
                        ),
                        # Ajustamos el eje X para que las etiquetas largas se lean bien
                        rx.recharts.x_axis(
                            data_key="categoria", 
                            angle=-45, 
                            text_anchor="end", 
                            height=100
                        ),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=DashboardState.categories_chart,
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
            ),
            style={"padding": "2em"}
        ),
        
        # 3. Gráfico: Bottom Estados
        rx.card(
            rx.vstack(
                rx.heading("📉 Bottom 10 Estados por Ventas", size="5"),
                rx.divider(),
                rx.cond(
                    DashboardState.has_data,
                    rx.recharts.composed_chart(
                        rx.recharts.bar(
                            data_key="ventas",
                            fill="#ff7c7c",
                        ),
                        rx.recharts.x_axis(data_key="estado"),
                        rx.recharts.y_axis(),
                        rx.recharts.tooltip(),
                        rx.recharts.legend(),
                        data=DashboardState.bottom_states_chart,
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
            ),
            style={"padding": "2em"}
        ),
        
        spacing="4",
        width="100%",
    )
    


def index() -> rx.Component:
    """Página principal del dashboard"""
    return rx.container(
        rx.vstack(
            # Header
            rx.hstack(
                rx.vstack(
                    rx.heading("📈 Dashboard Analytics", size="8"),
                    rx.text("Sistema de análisis de ventas con visualizaciones interactivas", size="4", color="gray"),
                    spacing="1",
                    align="start",
                ),
                rx.spacer(),
                rx.cond(
                    DashboardState.is_loading,
                    rx.spinner(size="3"),
                ),
                width="100%",
                align="center",
            ),
            
            rx.divider(size="4"),
            
            # Filtros
            filter_section(),
            
            # Métricas generales
            overview_metrics(),
            
            # Top performers
            top_performers(),
            
            # Gráficos
            charts_section(),
            
            # Estadísticas
            stats_grid("📊 Análisis Estadístico Descriptivo", DashboardState.statistics_data),
            
            spacing="5",
            width="100%",
            padding="2em",
        ),
        size="4",
    )


# Configuración de la app
app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="blue",
        gray_color="slate",
    )
)
app.add_page(index, on_load=DashboardState.on_mount)