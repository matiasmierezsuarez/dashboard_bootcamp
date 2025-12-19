"""Página de análisis de vendedores."""

import reflex as rx
from ..templates import template
from ..views.charts import (
    StatsState,
    sales_by_seller_chart,
    seller_chart_filters
)
from ..components.card import card

@template(
    route="/vendedores", 
    title="Vendedores", 
    on_load=[StatsState.load_sales_by_seller]
)
def vendedores() -> rx.Component:
    return rx.vstack(
        rx.heading("Top Vendedores", size="5"),
        
        card(
            rx.vstack(
                rx.hstack(
                    rx.heading("Ranking de Ventas por Vendedor (Top 10)", size="4"),
                    rx.spacer(),
                    seller_chart_filters(),
                    width="100%",
                    align="center"
                ),
                sales_by_seller_chart(),
                width="100%"
            )
        ),
        spacing="6",
        width="100%"
    )