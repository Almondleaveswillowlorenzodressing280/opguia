"""Browse page — top bar, search, full-screen tree-table, status bar."""

import asyncio
from nicegui import ui
from opguia.client import OpcuaClient
from opguia.components.tree_view import create_tree_view
from opguia.components.detail_panel import create_detail_panel


def register(client: OpcuaClient):
    @ui.page("/browse")
    async def browse_page():
        ui.dark_mode().enable()
        if not client.connected:
            ui.navigate.to("/")
            return

        # -- Top bar --
        with ui.header().classes(
            "items-center justify-between px-4 min-h-0 bg-gray-900 border-b border-gray-700"
        ).style("height:36px"):
            ui.label("OPC UA Browser").classes("text-sm font-bold")
            with ui.row().classes("items-center gap-3"):
                if client.server_name:
                    ui.label(f"Server: {client.server_name}").classes("text-xs text-gray-300")
                ui.icon("circle", size="8px").classes("text-green-400")

                async def do_disconnect():
                    await client.disconnect()
                    ui.navigate.to("/")
                ui.button("Disconnect", on_click=do_disconnect).props("flat dense size=xs color=red")

        # -- Search bar --
        with ui.row().classes(
            "w-full items-center px-4 bg-gray-900/80 border-b border-gray-700"
        ).style("height:34px; margin-top:36px"):
            ui.icon("search", size="16px").classes("text-gray-500")
            search_input = ui.input(placeholder="Filter nodes...").props(
                "dense borderless"
            ).classes("w-full text-xs").style("font-size:12px")

        # -- Tree (fills remaining space) --
        tree_scroll = ui.scroll_area().classes("w-full").style(
            "position:fixed; top:70px; bottom:28px; left:0; right:0"
        )
        with tree_scroll:
            tree_container, rebuild_tree, set_root = create_tree_view(
                client,
                on_select_node=lambda nid: show_detail_dialog(nid),
            )

        # -- Status bar --
        with ui.element("div").classes(
            "flex items-center gap-6 px-4 bg-gray-900 border-t border-gray-700 text-gray-500"
        ).style("position:fixed; bottom:0; left:0; right:0; height:28px; font-size:11px"):
            ui.label(client.endpoint).classes("font-mono")
            ui.label(f"Security: {client.security_policy}")
            latency_label = ui.label("Latency: ...")

        # -- Search filtering --
        async def on_search_change():
            query = search_input.value.strip().lower()
            await rebuild_tree(filter_query=query)

        search_input.on("keydown.enter", lambda: on_search_change())
        # Also filter on clear
        search_input.on("update:model-value", lambda e: on_search_change() if not search_input.value else None)

        # -- Latency polling --
        async def update_latency():
            while client.connected:
                ms = await client.measure_latency()
                if ms is not None:
                    latency_label.text = f"Latency: {ms} ms"
                await asyncio.sleep(5)
        asyncio.create_task(update_latency())

        # -- Detail dialog --
        async def show_detail_dialog(node_id: str):
            with ui.dialog().classes("w-full max-w-lg") as dlg, ui.card().classes("w-full p-4"):
                _container, show_details = create_detail_panel(
                    client,
                    on_set_root=lambda nid, name: _set_root_close(dlg, nid, name),
                )
            dlg.open()
            await show_details(node_id)

        async def _set_root_close(dlg, nid, name):
            dlg.close()
            await set_root(nid, name)

        await rebuild_tree()
