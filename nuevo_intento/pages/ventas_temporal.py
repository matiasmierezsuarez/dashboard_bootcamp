"""Página de análisis temporal de ventas."""

import reflex as rx
from ..templates import template
from ..views.charts import (
    StatsState,
    sales_year_chart,
    sales_month_chart,
    sales_time_chart,
    month_chart_filters,
    daily_chart_filters
)
from ..components.card import card

@template(
    route="/ventas_temporal", 
    title="Análisis Temporal", 
    on_load=[
        StatsState.load_sales_by_year, 
        StatsState.load_sales_by_month,
        StatsState.load_temporal_chart
    ]
)
def ventas_temporal() -> rx.Component:
    return rx.vstack(
        rx.heading("Análisis Temporal de Ventas", size="5"),
        
        card(
            rx.vstack(
                rx.heading("Ventas por Año", size="4"),
                sales_year_chart(),
                width="100%"
            )
        ),
        
        card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Ventas por Mes (Histórico)", size="4"),
                    rx.spacer(),
                    month_chart_filters(),
                    width="100%",
                    align="center"
                ),
                sales_month_chart(),
                width="100%"
            )
        ),
        
        card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Detalle Diario (Ventas por Día)", size="4"),
                    rx.spacer(),
                    daily_chart_filters(),
                    width="100%",
                    align="center"
                ),
                sales_time_chart(),
                width="100%"
            )
        ),
        spacing="6",
        width="100%"
    )
