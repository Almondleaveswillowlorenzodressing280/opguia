"""Graph panel — live time-series charts of watched variable values.

Displays one EChart per watched variable, stacked vertically in a
scrollable container. Each chart shows a single line with the variable
name, current value, and node ID.
"""

from nicegui import ui
from opguia.pages.browse.value_history import ValueHistory
from opguia.storage import Settings


def _make_chart_options(name: str, data: list) -> dict:
    return {
        "tooltip": {
            "trigger": "axis",
            "axisPointer": {"type": "cross"},
        },
        "grid": {"top": 8, "right": 16, "bottom": 24, "left": 52},
        "xAxis": {
            "type": "time",
            "axisLabel": {"color": "#6b7280", "fontSize": 10},
            "splitLine": {"show": False},
        },
        "yAxis": {
            "type": "value",
            "axisLabel": {"color": "#6b7280", "fontSize": 10},
            "splitLine": {"lineStyle": {"color": "#374151"}},
        },
        "series": [{
            "type": "line",
            "smooth": True,
            "showSymbol": False,
            "data": data,
            "lineStyle": {"width": 1.5},
            "areaStyle": {"opacity": 0.05},
        }],
    }


def create_graph_panel(settings: Settings, history: ValueHistory):
    """Create the graph panel. Returns (container, rebuild_fn, update_fn).

    rebuild_fn: call when watched list changes to recreate charts.
    update_fn:  call periodically to push latest history to charts.
    """
    container = ui.column().classes("w-full h-full gap-0")
    # {node_id: echart}
    _charts: dict[str, ui.echart] = {}
    # {node_id: label} for current value display
    _val_labels: dict[str, ui.label] = {}

    def rebuild():
        container.clear()
        _charts.clear()
        _val_labels.clear()
        watched = settings.watched
        with container:
            if not watched:
                with ui.column().classes("w-full h-full items-center justify-center"):
                    ui.icon("show_chart", size="48px").classes("text-gray-700")
                    ui.label("No watched variables").classes("text-sm text-gray-600")
                    ui.label("Star a variable in the tree to graph it here").classes(
                        "text-xs text-gray-700"
                    )
                return

            with ui.scroll_area().classes("w-full").style("flex:1; min-height:0"):
                with ui.column().classes("w-full gap-2 p-3"):
                    for item in watched:
                        nid = item["node_id"]
                        data = history.get(nid)
                        with ui.card().classes("w-full p-3").props("flat bordered"):
                            with ui.row().classes("items-center gap-2 w-full"):
                                ui.label(item["name"]).classes("text-xs font-medium")
                                val_lbl = ui.label("—").classes(
                                    "text-xs font-mono text-green-300"
                                )
                                _val_labels[nid] = val_lbl
                                ui.label(nid).classes(
                                    "text-xs font-mono text-gray-600 ml-auto truncate"
                                ).style("max-width:200px")
                            chart = ui.echart(
                                _make_chart_options(item["name"], data)
                            ).classes("w-full").style("height:150px")
                            _charts[nid] = chart

    def update():
        """Push latest history data to all charts."""
        for nid, chart in _charts.items():
            data = history.get(nid)
            chart.options["series"][0]["data"] = data
            chart.update()
            # Update current value label
            lbl = _val_labels.get(nid)
            if lbl and data:
                lbl.text = f"{data[-1][1]}"

    return container, rebuild, update
