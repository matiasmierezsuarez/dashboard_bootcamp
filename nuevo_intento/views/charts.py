import datetime
import random
import os
from asyncpg import Pool
import asyncpg
import reflex as rx
from dotenv import load_dotenv
from reflex.components.radix.themes.base import (
    LiteralAccentColor,
)
from ..components.card import card

_db_pool = None

class StatsState(rx.State):
    area_toggle: bool = True
    selected_tab: str = "estado"
    device_data:list[dict] = []
    line_data:list[dict] = []
    temporal_data: list[dict] = []
    start_date: str = "2018-08-04"
    end_date: str = "2018-09-03"
    sales_by_year_data: list[dict] = []
    sales_by_month_data: list[dict] = []
    
    month_chart_year: str = "2018"
    month_chart_month: str = "All"
    daily_chart_year: str = "2018"
    daily_chart_month: str = "08"
    daily_chart_day: str = "All"
    kpi_customers: int = 0
    kpi_sales: float = 0.0
    kpi_orders: int = 0
    seller_data: list[dict] = []
    seller_chart_year: str = "All"


    async def get_db_pool(self) -> Pool:
        global _db_pool
        if _db_pool is None:
            database_url = os.getenv("DATABASE_URL")
            _db_pool = await asyncpg.create_pool(database_url)
        return _db_pool

    @rx.event
    def set_selected_tab(self, tab: str | list[str]):
        self.selected_tab = tab if isinstance(tab, str) else tab[0]

    @rx.event
    def set_start_date(self, date: str):
        self.start_date = date
        return [StatsState.load_line_chart, StatsState.load_temporal_chart]

    @rx.event
    def set_end_date(self, date: str):
        self.end_date = date
        return [StatsState.load_line_chart, StatsState.load_temporal_chart]

    @rx.event
    def set_month_chart_year(self, value: str):
        self.month_chart_year = value
        return StatsState.load_sales_by_month

    @rx.event
    def set_month_chart_month(self, value: str):
        self.month_chart_month = value
        return StatsState.load_sales_by_month

    @rx.event
    def set_daily_chart_year(self, value: str):
        self.daily_chart_year = value
        return StatsState.load_temporal_chart

    @rx.event
    def set_daily_chart_month(self, value: str):
        self.daily_chart_month = value
        return StatsState.load_temporal_chart

    @rx.event
    def set_daily_chart_day(self, value: str):
        self.daily_chart_day = value
        return StatsState.load_temporal_chart

    @rx.event
    def set_seller_chart_year(self, value: str):
        self.seller_chart_year = value
        return StatsState.load_sales_by_seller

    def toggle_areachart(self):
        self.area_toggle = not self.area_toggle

    @rx.event
    async def load_line_chart(self):
        pool = await self.get_db_pool()

        group_map = {
            "estado": "c.customer_state",
            "ciudad": "c.customer_city",
            "categoria": "p.product_category_name",
        }

        group_field = group_map[self.selected_tab]

        query = f"""
            SELECT
                {group_field} AS label,
                SUM(f.total) AS ventas
            FROM gold.fact_sales f
            JOIN gold.dim_calendar cal ON f.date_purchase_key = cal.date_key
            JOIN gold.dim_customers c ON f.customer_key = c.customer_key
            JOIN gold.dim_products p ON f.product_key = p.product_key
            WHERE cal.date_ymd >= $1 AND cal.date_ymd <= $2
            GROUP BY label
            ORDER BY ventas DESC
            LIMIT 10
        """

        try:
            start = datetime.date.fromisoformat(self.start_date)
            end = datetime.date.fromisoformat(self.end_date)
        except ValueError:
            start = datetime.date(2018, 8, 28)
            end = datetime.date(2018, 9, 3)

        async with pool.acquire() as conn:
            rows = await conn.fetch(query, start, end)

        self.line_data = [
            {
                "Ventas": float(r["ventas"]),
                "Label": r["label"],
            }
            for r in rows
        ]

    @rx.event
    async def load_temporal_chart(self):
        pool = await self.get_db_pool()

        conditions = []
        args = []

        if self.daily_chart_year != "All":
            args.append(int(self.daily_chart_year))
            conditions.append(f"cal.date_year = ${len(args)}")
        
        if self.daily_chart_month != "All":
            args.append(int(self.daily_chart_month))
            conditions.append(f"cal.date_month = ${len(args)}")

        if self.daily_chart_day != "All":
            args.append(int(self.daily_chart_day))
            conditions.append(f"cal.date_day = ${len(args)}")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT
                cal.date_ymd AS date,
                SUM(f.total) AS ventas
            FROM gold.fact_sales f
            JOIN gold.dim_calendar cal ON f.date_purchase_key = cal.date_key
            {where_clause}
            GROUP BY cal.date_ymd
            ORDER BY cal.date_ymd;
        """

        async with pool.acquire() as conn:
            if args:
                rows = await conn.fetch(query, *args)
            else:
                rows = await conn.fetch(query)

        self.temporal_data = [
            {"date": str(r["date"]), "ventas": float(r["ventas"])}
            for r in rows
        ]

    @rx.event
    async def load_pie_chart(self):
        pool = await self.get_db_pool()

        query = f"""
            SELECT
                cal.date_year AS label,
                SUM(f.total) AS ventas
            FROM gold.fact_sales f
            JOIN gold.dim_calendar cal ON f.date_purchase_key = cal.date_key
            GROUP BY label
            ORDER BY label;
        """

        async with pool.acquire() as conn:
            rows = await conn.fetch(query)

        colors = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884d8", "#82ca9d"]

        self.device_data = [
            {
                "name": str(r["label"]),
                "value": round(float(r["ventas"]), 2),
                "fill": colors[i % len(colors)],
            }
            for i, r in enumerate(rows)
        ]


    @rx.event
    async def load_sales_by_year(self):
        pool = await self.get_db_pool()
        query = """
            SELECT
                cal.date_year,
                SUM(f.total) AS ventas
            FROM gold.fact_sales f
            JOIN gold.dim_calendar cal ON f.date_purchase_key = cal.date_key
            GROUP BY cal.date_year
            ORDER BY cal.date_year;
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(query)
        
        self.sales_by_year_data = [
            {"name": str(r["date_year"]), "ventas": float(r["ventas"])}
            for r in rows
        ]

    @rx.event
    async def load_sales_by_month(self):
        pool = await self.get_db_pool()
        
        conditions = []
        args = []

        if self.month_chart_year != "All":
            args.append(int(self.month_chart_year))
            conditions.append(f"cal.date_year = ${len(args)}")
        
        if self.month_chart_month != "All":
            args.append(int(self.month_chart_month))
            conditions.append(f"cal.date_month = ${len(args)}")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT
                cal.date_year,
                cal.date_month,
                SUM(f.total) AS ventas
            FROM gold.fact_sales f
            JOIN gold.dim_calendar cal ON f.date_purchase_key = cal.date_key
            {where_clause}
            GROUP BY cal.date_year, cal.date_month
            ORDER BY cal.date_year, cal.date_month;
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args) if args else await conn.fetch(query)
        
        # Formato YYYY-MM para el eje X
        self.sales_by_month_data = [
            {
                "name": f"{r['date_year']}-{str(r['date_month']).zfill(2)}", 
                "ventas": float(r["ventas"])
            }
            for r in rows
        ]

    @rx.event
    async def load_kpi_data(self):
        pool = await self.get_db_pool()
        async with pool.acquire() as conn:
            self.kpi_customers = await conn.fetchval("SELECT COUNT(*) FROM gold.dim_customers") or 0
            self.kpi_sales = float(await conn.fetchval("SELECT SUM(total) FROM gold.fact_sales") or 0.0)
            self.kpi_orders = await conn.fetchval("SELECT COUNT(DISTINCT order_id) FROM gold.fact_sales") or 0

    @rx.event
    async def load_sales_by_seller(self):
        pool = await self.get_db_pool()
        
        conditions = []
        args = []

        if self.seller_chart_year != "All":
            args.append(int(self.seller_chart_year))
            conditions.append(f"cal.date_year = ${len(args)}")

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT
                s.seller_id,
                SUM(f.total) AS ventas
            FROM gold.fact_sales f
            JOIN gold.dim_sellers s ON f.seller_key = s.seller_key
            JOIN gold.dim_calendar cal ON f.date_purchase_key = cal.date_key
            {where_clause}
            GROUP BY s.seller_id
            ORDER BY ventas DESC
            LIMIT 10;
        """
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, *args) if args else await conn.fetch(query)
        
        self.seller_data = [
            {"name": str(r["seller_id"]), "ventas": float(r["ventas"])}
            for r in rows
        ]



def area_toggle() -> rx.Component:
    return rx.cond(
        StatsState.area_toggle,
        rx.icon_button(
            rx.icon("area-chart"),
            size="2",
            cursor="pointer",
            variant="surface",
            on_click=StatsState.toggle_areachart,
        ),
        rx.icon_button(
            rx.icon("bar-chart-3"),
            size="2",
            cursor="pointer",
            variant="surface",
            on_click=StatsState.toggle_areachart,
        ),
    )


def _create_gradient(color: LiteralAccentColor, id: str) -> rx.Component:
    return (
        rx.el.svg.defs(
            rx.el.svg.linear_gradient(
                rx.el.svg.stop(
                    stop_color=rx.color(color, 7), offset="5%", stop_opacity=0.8
                ),
                rx.el.svg.stop(
                    stop_color=rx.color(color, 7), offset="95%", stop_opacity=0
                ),
                x1=0,
                x2=0,
                y1=0,
                y2=1,
                id=id,
            ),
        )
    )


def _custom_tooltip(color: LiteralAccentColor) -> rx.Component:
    return (
        rx.recharts.graphing_tooltip(
            separator=" : ",
            content_style={
                "backgroundColor": rx.color("gray", 1),
                "borderRadius": "var(--radius-2)",
                "borderWidth": "1px",
                "borderColor": rx.color(color, 7),
                "padding": "0.5rem",
                "boxShadow": "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)",
            },
            is_animation_active=True,
        )
    )


def _render_area_chart(color: LiteralAccentColor, gradient_id: str) -> rx.Component:
    return rx.recharts.area_chart(
        _create_gradient(color, gradient_id),
        _custom_tooltip(color),
        rx.recharts.cartesian_grid(
            stroke_dasharray="3 3",
        ),
        rx.recharts.area(
            data_key="Ventas",
            stroke=rx.color(color, 9),
            fill=f"url(#{gradient_id})",
            type_="monotone",
        ),
        rx.recharts.x_axis(data_key="Label", scale="auto"),
        rx.recharts.y_axis(),
        rx.recharts.legend(),
        data=StatsState.line_data,
        height=425,
        width="100%",
    )


def _render_bar_chart(color: LiteralAccentColor) -> rx.Component:
    return rx.recharts.bar_chart(
        _custom_tooltip(color),
        rx.recharts.cartesian_grid(
            stroke_dasharray="3 3",
        ),
        rx.recharts.bar(
            data_key="Ventas",
            stroke=rx.color(color, 9),
            fill=rx.color(color, 7),
        ),
        rx.recharts.x_axis(data_key="Label", type_="category"),
        rx.recharts.y_axis(type_="number"),
        rx.recharts.legend(),
        data=StatsState.line_data,
        height=425,
        width="100%",
    )


def estado_chart() -> rx.Component:
    return rx.cond(
        StatsState.area_toggle,
        _render_area_chart("blue", "colorBlue"),
        _render_bar_chart("blue"),
    )


def ciudad_chart() -> rx.Component:
    return rx.cond(
        StatsState.area_toggle,
        _render_area_chart("green", "colorGreen"),
        _render_bar_chart("green"),
    )


def categoria_chart() -> rx.Component:
    return rx.cond(
        StatsState.area_toggle,
        _render_area_chart("purple", "colorPurple"),
        _render_bar_chart("purple"),
    )


def sales_time_chart() -> rx.Component:
    return rx.recharts.area_chart(
        _create_gradient("blue", "colorTemporal"),
        _custom_tooltip("blue"),
        rx.recharts.cartesian_grid(
            stroke_dasharray="3 3",
        ),
        rx.recharts.area(
            data_key="ventas",
            stroke=rx.color("blue", 9),
            fill="url(#colorTemporal)",
            type_="monotone",
        ),
        rx.recharts.x_axis(data_key="date", scale="auto"),
        rx.recharts.y_axis(),
        rx.recharts.legend(),
        data=StatsState.temporal_data,
        height=300,
        width="100%",
    )


def sales_year_chart() -> rx.Component:
    return rx.recharts.bar_chart(
        _custom_tooltip("blue"),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.bar(
            data_key="ventas",
            fill=rx.color("blue", 9),
            radius=[4, 4, 0, 0],
        ),
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(),
        rx.recharts.legend(),
        data=StatsState.sales_by_year_data,
        height=300,
        width="100%",
    )


def sales_month_chart() -> rx.Component:
    return rx.recharts.area_chart(
        _create_gradient("purple", "colorMonth"),
        _custom_tooltip("purple"),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.area(
            data_key="ventas",
            stroke=rx.color("purple", 9),
            fill="url(#colorMonth)",
            type_="monotone",
        ),
        rx.recharts.x_axis(data_key="name"),
        rx.recharts.y_axis(),
        rx.recharts.legend(),
        data=StatsState.sales_by_month_data,
        height=300,
        width="100%",
    )


def pie_chart() -> rx.Component:
    return rx.recharts.pie_chart(
        rx.recharts.pie(
            data=StatsState.device_data,
            data_key="value",
            name_key="name",
            cx="50%",
            cy="50%",
            padding_angle=1,
            inner_radius="70",
            outer_radius="100",
            label=True,
        ),
        rx.recharts.legend(),
        rx.recharts.graphing_tooltip(separator=": $"),
        height=300,
        width="100%",
    )


def date_filter() -> rx.Component:
    return rx.hstack(
        rx.icon("calendar", size=20, color=rx.color("gray", 10)),
        rx.input(
            type="date",
            value=StatsState.start_date,
            on_change=StatsState.set_start_date,
            size="2",
        ),
        rx.text("-", size="2", color=rx.color("gray", 10)),
        rx.input(
            type="date",
            value=StatsState.end_date,
            on_change=StatsState.set_end_date,
            size="2",
        ),
        align="center",
        spacing="2",
    )

def month_chart_filters() -> rx.Component:
    years = ["All", "2016", "2017", "2018"]
    months = ["All"] + [str(i).zfill(2) for i in range(1, 13)]
    return rx.hstack(
        rx.text("Año:", weight="medium"),
        rx.select(
            years, 
            value=StatsState.month_chart_year, 
            on_change=StatsState.set_month_chart_year
        ),
        rx.text("Mes:", weight="medium"),
        rx.select(
            months, 
            value=StatsState.month_chart_month, 
            on_change=StatsState.set_month_chart_month
        ),
        spacing="3",
        align="center"
    )

def sales_by_seller_chart() -> rx.Component:
    return rx.recharts.bar_chart(
        _custom_tooltip("blue"),
        rx.recharts.cartesian_grid(stroke_dasharray="3 3"),
        rx.recharts.bar(
            data_key="ventas",
            fill=rx.color("blue", 9),
            radius=[0, 4, 4, 0],
        ),
        rx.recharts.x_axis(type_="number"),
        rx.recharts.y_axis(data_key="name", type_="category", width=150),
        rx.recharts.legend(),
        data=StatsState.seller_data,
        layout="vertical",
        height=500,
        width="100%",
    )

def seller_chart_filters() -> rx.Component:
    years = ["All", "2016", "2017", "2018"]
    return rx.hstack(
        rx.text("Año:", weight="medium"),
        rx.select(
            years, 
            value=StatsState.seller_chart_year, 
            on_change=StatsState.set_seller_chart_year
        ),
        spacing="3",
        align="center"
    )

def stats_cards() -> rx.Component:
    return rx.grid(
        card(
            rx.vstack(
                rx.hstack(
                    rx.icon("users", size=20),
                    rx.text("Total Clientes", size="4", weight="medium"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(f"{StatsState.kpi_customers:,}", size="6"),
                width="100%",
            )
        ),
        card(
            rx.vstack(
                rx.hstack(
                    rx.icon("dollar-sign", size=20),
                    rx.text("Total Ventas", size="4", weight="medium"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(f"${StatsState.kpi_sales:,.2f}", size="6"),
                width="100%",
            )
        ),
        card(
            rx.vstack(
                rx.hstack(
                    rx.icon("shopping-cart", size=20),
                    rx.text("Total Ordenes", size="4", weight="medium"),
                    align="center",
                    spacing="2",
                ),
                rx.heading(f"{StatsState.kpi_orders:,}", size="6"),
                width="100%",
            )
        ),
        gap="1rem",
        grid_template_columns=["1fr", "repeat(3, 1fr)"],
        width="100%",
    )

def daily_chart_filters() -> rx.Component:
    years = ["All", "2016", "2017", "2018"]
    months = ["All"] + [str(i).zfill(2) for i in range(1, 13)]
    days = ["All"] + [str(i).zfill(2) for i in range(1, 32)]
    return rx.hstack(
        rx.text("Año:", weight="medium"),
        rx.select(years, value=StatsState.daily_chart_year, on_change=StatsState.set_daily_chart_year),
        
        rx.text("Mes:", weight="medium"),
        rx.select(months, value=StatsState.daily_chart_month, on_change=StatsState.set_daily_chart_month),
        
        rx.text("Día:", weight="medium"),
        rx.select(days, value=StatsState.daily_chart_day, on_change=StatsState.set_daily_chart_day),
        
        spacing="3",
        align="center"
    )
