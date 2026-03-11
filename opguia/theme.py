"""Centralized theme — colors, shared CSS, and page setup helpers.

Uses NiceGUI's ui.colors() for Quasar palette and ui.add_css() for custom
styles. Import `apply_theme()` at the top of each @ui.page function.
"""

from nicegui import ui

# ── Color palette (Material Dark) ──

BACKGROUND = "#121212"
SURFACE = "#1e1e1e"
SURFACE_BRIGHT = "#2c2c2c"
TEXT = "#e3e3e3"
MUTED = "#9e9e9e"

# Quasar palette overrides (applied via ui.colors)
COLORS = {
    "primary": "#3d7bd9",
    "secondary": "#9b6ddb",
    "accent": "#03b5a3",
    "dark": SURFACE,
    "dark-page": BACKGROUND,
    "positive": "#5a9e6f",
    "negative": "#cf6679",
    "info": "#5c8abf",
    "warning": "#c9a84c",
}

# ── Shared CSS ──

_CSS = f"""
html, body {{
    background: {BACKGROUND} !important;
}}
/* Smooth page transitions */
.nicegui-content {{
    animation: fadeIn 0.15s ease-in;
}}
@keyframes fadeIn {{
    from {{ opacity: 0; }}
    to {{ opacity: 1; }}
}}
/* Scrollbar styling */
::-webkit-scrollbar {{
    width: 6px;
    height: 6px;
}}
::-webkit-scrollbar-track {{
    background: transparent;
}}
::-webkit-scrollbar-thumb {{
    background: #ffffff20;
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{
    background: #ffffff40;
}}
"""


def apply_theme():
    """Call at the top of every @ui.page to apply consistent theming."""
    ui.dark_mode().enable()
    ui.colors(**COLORS)
    ui.add_css(_CSS)
    ui.query("body").style("margin:0; overflow:hidden")
    ui.query(".nicegui-content").classes("w-full h-screen").style(
        "display:flex; flex-direction:column; padding:0; gap:0"
    )
