"""Application entry point — wires up pages and runs NiceGUI."""

from nicegui import ui
from opguia.client import OpcuaClient
from opguia.settings import Settings
from opguia.pages import connection, browse


def run():
    client = OpcuaClient()
    settings = Settings()
    connection.register(client, settings)
    browse.register(client, settings)
    ui.run(
        title="OPGuia",
        favicon="🔌",
        port=8080,
        reload=False,
        storage_secret="opguia",
        native=True,
        window_size=(1200, 800),
    )
