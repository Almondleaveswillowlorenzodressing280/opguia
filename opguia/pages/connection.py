"""Connection page — endpoint input, server scan, connect.

Landing page at "/". Shows an endpoint input field, saved connections,
and auto-scans for local OPC UA servers on common ports.
"""

import asyncio
from nicegui import ui
from opguia.client import OpcuaClient
from opguia.scanner import scan_servers
from opguia.settings import Settings


def register(client: OpcuaClient, settings: Settings):
    @ui.page("/")
    async def connection_page():
        ui.dark_mode().enable()
        with ui.column().classes("w-full items-center justify-center min-h-screen gap-4"):
            ui.label("OPGuia").classes("text-3xl font-bold")

            # Manual endpoint input
            with ui.card().classes("w-96 p-4"):
                endpoint = ui.input("Endpoint", value="opc.tcp://localhost:4840").classes("w-full")
                status = ui.label("").classes("text-xs")

                async def do_connect():
                    status.text = "Connecting..."
                    status.classes(remove="text-red-400 text-green-400")
                    try:
                        await client.connect(endpoint.value)
                        status.text = "Connected"
                        status.classes(add="text-green-400")
                        await asyncio.sleep(0.3)
                        ui.navigate.to("/browse")
                    except Exception as e:
                        status.text = str(e)
                        status.classes(add="text-red-400")

                with ui.row().classes("w-full gap-2"):
                    ui.button("Connect", on_click=do_connect).classes("flex-grow")
                    ui.button(
                        icon="bookmark_add",
                        on_click=lambda: save_connection(endpoint.value),
                    ).props("flat dense").tooltip("Save connection")

            # Saved connections
            saved_card = ui.card().classes("w-96 p-4")

            def render_saved():
                saved_card.clear()
                with saved_card:
                    ui.label("Saved Connections").classes("text-sm font-bold")
                    conns = settings.connections
                    if not conns:
                        ui.label("No saved connections").classes("text-xs text-gray-500 mt-1")
                    else:
                        with ui.column().classes("w-full gap-1 mt-2"):
                            for url in conns:
                                with ui.row().classes(
                                    "items-center gap-2 w-full hover:bg-gray-800 rounded px-2 py-1"
                                ):
                                    pick_row = ui.row().classes(
                                        "items-center gap-2 flex-grow cursor-pointer min-w-0"
                                    )
                                    with pick_row:
                                        ui.icon("bookmark", size="14px").classes("text-blue-400 shrink-0")
                                        ui.label(url).classes("text-xs font-mono truncate")

                                    def pick(u=url):
                                        endpoint.value = u
                                    pick_row.on("click", pick)

                                    def remove(u=url):
                                        settings.remove_connection(u)
                                        render_saved()

                                    ui.button(
                                        icon="close", on_click=remove,
                                    ).props("flat dense round size=xs").classes("text-gray-500 shrink-0")

            def save_connection(url: str):
                settings.add_connection(url)
                render_saved()

            render_saved()

            # Auto-discovered servers
            with ui.card().classes("w-96 p-4"):
                with ui.row().classes("items-center justify-between w-full"):
                    ui.label("Discovered Servers").classes("text-sm font-bold")
                    scan_spinner = ui.spinner(size="sm")
                scan_list = ui.column().classes("w-full gap-1 mt-2")

            async def run_scan():
                scan_list.clear()
                scan_spinner.visible = True
                servers = await scan_servers()
                scan_spinner.visible = False
                with scan_list:
                    if not servers:
                        ui.label("No servers found").classes("text-xs text-gray-500")
                    for srv in servers:
                        with ui.row().classes(
                            "items-center gap-2 w-full hover:bg-gray-800 rounded px-2 py-1 cursor-pointer"
                        ) as row:
                            ui.icon("dns", size="14px").classes("text-green-400")
                            with ui.column().classes("gap-0"):
                                ui.label(srv["name"] or "OPC UA Server").classes("text-xs font-bold")
                                ui.label(srv["url"]).classes("text-xs text-gray-400 font-mono")

                            def pick(url=srv["url"]):
                                endpoint.value = url
                            row.on("click", pick)

            asyncio.create_task(run_scan())
            ui.timer(5.0, run_scan)

            # Show existing connection if already connected
            if client.connected:
                with ui.row().classes("items-center gap-1"):
                    ui.icon("check_circle", size="xs").classes("text-green-400")
                    ui.label(client.endpoint).classes("text-xs text-green-400")
                    ui.button("Browse", on_click=lambda: ui.navigate.to("/browse")).props("flat dense size=sm")
