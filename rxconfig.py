import reflex as rx

config = rx.Config(

    app_name="nuevo_intento",

    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
    ]
)