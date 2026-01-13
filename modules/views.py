# Facade for backward compatibility
# Re-exports functions from the new split modules

from modules.views_citizen import render_citizen_view
from modules.views_official import render_official_view, render_field_ops_view
# render_field_ops_card_grid is now in ui.py but views_official re-exports the view that uses it.
# If anything imports it from here, we should re-export it.
from modules.ui import render_field_ops_card_grid

# Ensure no other functions are missing that were widely used.
# The original file had: 'render_citizen_view', 'render_official_view', 'render_field_ops_view', 'render_field_ops_card_grid'.
# All covered.
