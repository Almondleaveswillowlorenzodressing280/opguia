"""Tree-table view — compact rows, aligned columns, filter support."""

from nicegui import ui
from opguia.client import OpcuaClient

_STATUS = {"good": "text-green-500", "warning": "text-yellow-400", "bad": "text-red-500"}

_TYPE_COLORS = {
    "Boolean": "text-green-500", "Float": "text-blue-400", "Double": "text-blue-400",
    "Int16": "text-orange-400", "Int32": "text-orange-400", "Int64": "text-orange-400",
    "UInt16": "text-orange-400", "UInt32": "text-orange-400", "UInt64": "text-orange-400",
    "Byte": "text-orange-400", "String": "text-teal-400",
}

_TYPE_ICONS = {
    "Boolean": "toggle_on", "Float": "tag", "Double": "tag",
    "Int16": "tag", "Int32": "tag", "Int64": "tag",
    "UInt16": "tag", "UInt32": "tag", "UInt64": "tag",
    "Byte": "tag", "String": "text_fields",
}

# Row height
_H = "26px"


def create_tree_view(client: OpcuaClient, on_select_node):
    """Returns (container, rebuild_fn, set_root_fn)."""
    root_state = {"node_id": None, "path": []}
    tree_container = ui.column().classes("w-full gap-0 select-none")

    async def set_root(node_id: str | None, name: str | None = None):
        if node_id is None:
            root_state["node_id"] = None
            root_state["path"] = []
        else:
            root_state["node_id"] = node_id
            if name:
                root_state["path"].append(name)
        await rebuild_tree()

    async def rebuild_tree(filter_query: str = ""):
        tree_container.clear()
        with tree_container:
            # Root row
            root_expanded = {"value": True}
            root_row = _make_row(0)
            with root_row:
                root_arrow = ui.icon("expand_more", size="14px").classes("text-gray-500")
                ui.icon("folder", size="14px").classes("text-blue-300")
                name = "Objects"
                if root_state["path"]:
                    name += " / " + " / ".join(root_state["path"])
                ui.label(name).classes("text-xs font-medium")

            root_children = ui.column().classes("w-full gap-0")

            async def toggle_root():
                if root_expanded["value"]:
                    root_expanded["value"] = False
                    root_arrow.props("name=chevron_right")
                    root_children.clear()
                else:
                    root_expanded["value"] = True
                    root_arrow.props("name=expand_more")
                    await _load(root_children, root_state["node_id"], 1, filter_query)

            root_row.on("click", lambda: toggle_root())
            await _load(root_children, root_state["node_id"], 1, filter_query)

    async def _load(container, node_id, depth, fq):
        with container:
            sp = ui.spinner(size="xs").classes("ml-6")
        try:
            children = await client.browse_children(node_id)
        except Exception as e:
            container.clear()
            with container:
                ui.label(f"Error: {e}").classes("text-red-400 text-xs ml-6")
            return

        sp.delete()

        # Filter
        if fq:
            children = [c for c in children if _matches(c, fq)]

        if not children:
            with container:
                ui.label("(empty)").classes("text-gray-600").style(
                    f"font-size:11px; padding-left:{depth * 20 + 30}px; height:{_H}; line-height:{_H}"
                )
            return

        for node in children:
            with container:
                _render(node, depth, fq)

    def _matches(node, fq):
        """Check if node or its name matches filter query."""
        name = node["name"].lower()
        # Support dot-separated path-like queries
        parts = fq.split(".")
        return all(p in name for p in parts)

    def _render(node, depth, fq):
        indent = depth * 20
        has_ch = node.get("has_children", False)

        if node["is_variable"]:
            dt = node.get("data_type", "")
            icon = _TYPE_ICONS.get(dt, "data_object")
            icon_color = _TYPE_COLORS.get(dt, "text-gray-400")
            st_color = _STATUS.get(node.get("status", "good"), "text-gray-500")

            row = _make_row(indent)
            with row:
                # Arrow or spacer
                if has_ch:
                    arrow = ui.icon("chevron_right", size="14px").classes("text-gray-500 transition-transform")
                else:
                    ui.element("div").style("width:14px; flex-shrink:0")

                # Icon
                ui.icon(icon, size="14px").classes(icon_color)

                # Name (flexible)
                ui.label(node["name"]).classes("text-xs font-medium truncate").style("min-width:120px; flex:1")

                # Value (fixed width, right-aligned)
                val = node["value"]
                if val is not None and val != "?":
                    val_text = str(val)
                    if len(val_text) > 30:
                        val_text = val_text[:30] + ".."
                    ui.label(val_text).classes("text-xs font-mono text-gray-200 text-right truncate").style(
                        "width:140px; flex-shrink:0"
                    )
                else:
                    ui.element("div").style("width:140px; flex-shrink:0")

                # Type
                if dt:
                    ui.label(dt).classes("text-xs text-gray-500 text-right").style(
                        "width:60px; flex-shrink:0"
                    )
                else:
                    ui.element("div").style("width:60px; flex-shrink:0")

                # Status dot
                ui.icon("circle", size="8px").classes(st_color).style("width:20px; flex-shrink:0")

            if has_ch:
                child_ct = ui.column().classes("w-full gap-0")
                exp = {"v": False}

                async def toggle(nid=node["id"], ct=child_ct, ar=arrow, ex=exp, d=depth):
                    if not ex["v"]:
                        ex["v"] = True
                        ar.classes(add="rotate-90")
                        await _load(ct, nid, d + 1, fq)
                    else:
                        ex["v"] = False
                        ar.classes(remove="rotate-90")
                        ct.clear()

                row.on("click", lambda nid=node["id"]: toggle(nid))
                row.on("dblclick", lambda nid=node["id"]: on_select_node(nid))
            else:
                row.on("click", lambda nid=node["id"]: on_select_node(nid))

        elif node.get("is_method"):
            row = _make_row(indent)
            with row:
                ui.element("div").style("width:14px; flex-shrink:0")
                ui.icon("settings", size="14px").classes("text-purple-400")
                ui.label(node["name"]).classes("text-xs text-gray-500")

        else:
            # Folder / object
            exp = {"v": False}
            row = _make_row(indent)
            with row:
                arrow = ui.icon("chevron_right", size="14px").classes("text-gray-500 transition-transform")
                ui.icon("folder", size="14px").classes("text-yellow-500")
                ui.label(node["name"]).classes("text-xs font-medium")

            child_ct = ui.column().classes("w-full gap-0")

            async def toggle_f(nid=node["id"], ct=child_ct, ar=arrow, ex=exp, d=depth):
                if not ex["v"]:
                    ex["v"] = True
                    ar.classes(add="rotate-90")
                    await _load(ct, nid, d + 1, fq)
                else:
                    ex["v"] = False
                    ar.classes(remove="rotate-90")
                    ct.clear()

            row.on("click", lambda nid=node["id"]: toggle_f(nid))
            row.on("dblclick", lambda nid=node["id"]: on_select_node(nid))

    return tree_container, rebuild_tree, set_root


def _make_row(indent: int):
    """Create a compact tree row with proper indent."""
    return ui.row().classes(
        "items-center gap-1.5 px-3 hover:bg-white/5 cursor-pointer w-full"
    ).style(f"height:{_H}; padding-left:{indent}px")
