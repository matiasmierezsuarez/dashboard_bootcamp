"""
Dashboard Analytics - Archivo Principal
Versión Modularizada
"""
import reflex as rx
from .state import DashboardState
from .components import navbar, global_filters_section
from .pages import (
    overview_page,
    charts_page,
    analysis_page,
    statistics_page,
    temporal_analysis_page
)


# ==================== COMPONENTE PRINCIPAL ====================

def index() -> rx.Component:
    """Página principal del dashboard"""
    return rx.box(
        navbar(DashboardState),
        rx.container(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.vstack(
                        rx.heading("Dashboard Analytics - Versión Mejorada", size="8"),
                        rx.text("Sistema de análisis con filtros globales y navegación por secciones", size="4", color="gray"),
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
                
                # Filtros globales
                global_filters_section(DashboardState),
                
                # Contenido según página activa
                rx.cond(
                    DashboardState.current_page == "overview",
                    overview_page(DashboardState),
                ),
                rx.cond(
                    DashboardState.current_page == "charts",
                    charts_page(DashboardState),
                ),
                rx.cond(
                    DashboardState.current_page == "analysis",
                    analysis_page(DashboardState),
                ),
                rx.cond(
                    DashboardState.current_page == "statistics",
                    statistics_page(DashboardState),
                ),
                rx.cond(
                    DashboardState.current_page == "temporal",
                    temporal_analysis_page(DashboardState),
                ),
                
                spacing="5",
                width="100%",
                padding="2em",
            ),
            size="4",
        ),
    )


# ==================== CONFIGURACIÓN DE LA APP ====================

app = rx.App(
    theme=rx.theme(
        appearance="dark",
        accent_color="gray",
        gray_color="slate",
    )
)
app.add_page(index, on_load=DashboardState.on_mount)