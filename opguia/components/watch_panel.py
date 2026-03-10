"""Watch panel — always-visible live variable values.

Displays watched variables in a compact table at the bottom of the browse
page. Values are polled every 2s alongside the tree view polling.
"""

from nicegui import ui
from opguia.client import OpcuaClient
from opguia.settings import Settings


def create_watch_panel(
    client: OpcuaClient,
    settings: Settings,
    on_select_node=None,
    on_watch_changed=None,
):
    """Create the watch panel. Returns (container, render_fn, poll_fn).

    render_fn: call to rebuild the watch list from settings.
    poll_fn:   call periodically to update values.
    """
    container = ui.column().classes("w-full gap-0")

    # {node_id: value_label} for live polling
    _labels: dict[str, ui.label] = {}

    def render():
        container.clear()
        _labels.clear()
        watched = settings.watched
        with container:
            if not watched:
                ui.label("No watched variables — star a variable to add it here").classes(
                    "text-xs text-gray-600 px-3 py-2"
                )
                return

            # Header row
            with ui.row().classes(
                "items-center gap-2 w-full px-3 border-b border-gray-700"
            ).style("height:22px"):
                ui.label("Name").classes("text-xs text-gray-500 font-medium").style(
                    "width:180px; flex-shrink:0"
                )
                ui.label("Value").classes("text-xs text-gray-500 font-medium flex-grow")
                ui.label("Node ID").classes("text-xs text-gray-500 font-medium").style(
                    "width:200px; flex-shrink:0"
                )
                ui.element("div").style("width:28px; flex-shrink:0")

            for item in watched:
                nid = item["node_id"]
                name = item["name"]

                with ui.row().classes(
                    "items-center gap-2 w-full px-3 hover:bg-white/5 cursor-pointer"
                ).style("height:24px") as row:
                    # Name
                    ui.label(name).classes("text-xs font-medium truncate").style(
                        "width:180px; flex-shrink:0"
                    )
                    # Value (polled)
                    val_lbl = ui.label("...").classes(
                        "text-xs font-mono text-green-300 truncate flex-grow"
                    )
                    _labels[nid] = val_lbl
                    # Node ID
                    ui.label(nid).classes("text-xs font-mono text-gray-600 truncate").style(
                        "width:200px; flex-shrink:0"
                    )
                    # Remove button

                    def remove(node_id=nid):
                        settings.remove_watched(node_id)
                        render()
                        if on_watch_changed:
                            on_watch_changed()

                    ui.button(icon="close", on_click=remove).props(
                        "flat dense round size=xs"
                    ).classes("text-gray-600 shrink-0").style("opacity:0.5")

                if on_select_node:
                    row.on("click", lambda n=nid: on_select_node(n))

    async def poll():
        if not _labels or not client.connected:
            return
        for nid, lbl in list(_labels.items()):
            try:
                val = await client.read_value(nid)
                val_text = str(val) if val is not None else "—"
                if len(val_text) > 60:
                    val_text = val_text[:60] + ".."
                lbl.text = val_text
            except Exception as e:
                lbl.text = f"Error: {e}"
                lbl.classes(remove="text-green-300", add="text-red-400")

    return container, render, poll
