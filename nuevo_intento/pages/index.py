"""The overview page of the app."""

import reflex as rx

from .. import styles
from ..components.card import card
from ..components.notification import notification
from ..templates import template
from ..views.charts import (
    StatsState,
    area_toggle,
    categoria_chart,
    pie_chart,
    ciudad_chart,
    estado_chart,
    date_filter,
    stats_cards,
)


def tab_content_header() -> rx.Component:
    return rx.hstack(
        date_filter(),
        area_toggle(),
        align="center",
        width="100%",
        spacing="4",
    )


@template(route="/", title="Dashboard", on_load=[StatsState.load_line_chart, StatsState.load_pie_chart, StatsState.load_kpi_data],)
def index() -> rx.Component:
    """The overview page.

    Returns:
        The UI for the overview page.

    """
    return rx.vstack(
        rx.heading(f"Welcome", size="5"),
        stats_cards(),
        card(
            rx.hstack(
                tab_content_header(),
                rx.segmented_control.root(
                    rx.segmented_control.item("Estado", value="estado"),
                    rx.segmented_control.item("Ciudad", value="ciudad"),
                    rx.segmented_control.item("Categoria", value="categoria"),
                    margin_bottom="1.5em",
                    default_value="Estado",
                    on_change=[StatsState.set_selected_tab,
                               StatsState.load_line_chart],
                ),
                width="100%",
                justify="between",
            ),
            rx.match(
                StatsState.selected_tab,
                ("estado", estado_chart()),
                ("ciudad", ciudad_chart()),
                ("categoria", categoria_chart()),
            ),
        ),
        rx.center(
            rx.box(
                card(
                    rx.hstack(
                        rx.hstack(
                            rx.icon("user-round-search", size=20),
                            rx.text("Ventas", size="4", weight="medium"),
                            align="center",
                            spacing="2",
                        ),
                        align="center",
                        width="100%",
                        justify="between",
                    ),
                    pie_chart(),
                ),
                width="50%",
            ),
            width="100%",
        ),
        spacing="8",
        width="100%",
    )
