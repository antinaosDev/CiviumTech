import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from modules.ui import COLOR_MID_BLUE, COLOR_LIGHT_BLUE, COLOR_PRIMARY_GREEN, COLOR_DARK_BLUE

def plot_bar_chart(df, x, y, title, color_col=None, orientation='v'):
    """Generates a standardized bar chart."""
    fig = px.bar(
        df, 
        x=x, 
        y=y, 
        color=color_col if color_col else x,
        title=title,
        text_auto=True,
        orientation=orientation,
        color_discrete_sequence=[COLOR_MID_BLUE, COLOR_LIGHT_BLUE, COLOR_DARK_BLUE]
    )
    fig.update_traces(hovertemplate="<b>%{label}</b><br>Valor: %{value}<extra></extra>") # Generic Spanish tooltip
    fig.update_layout(
        template="plotly_white",
        margin=dict(t=40, b=0, l=0, r=0),
        font=dict(family="Inter"),
        showlegend=False
    )
    return fig

def plot_donut_chart(df, names, values, title):
    """Generates a standardized donut chart."""
    fig = px.pie(
        df, 
        names=names, 
        values=values, 
        title=title, 
        hole=0.5,
        color_discrete_sequence=[COLOR_MID_BLUE, COLOR_PRIMARY_GREEN, "#FFD700", "#FF6B6B"]
    )
    fig.update_traces(textposition='inside', textinfo='percent+label', hovertemplate="<b>%{label}</b><br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>")
    fig.update_layout(
        template="plotly_white",
        margin=dict(t=40, b=0, l=0, r=0),
        font=dict(family="Inter"),
        showlegend=False
    )
    return fig

def plot_line_chart(df, x, y, title):
    """Generates a smooth line chart."""
    fig = px.line(
        df, 
        x=x, 
        y=y, 
        title=title,
        markers=True
    )
    fig.update_traces(line_color=COLOR_MID_BLUE, line_shape='spline', hovertemplate="<b>%{x}</b><br>Valor: %{y}<extra></extra>")
    fig.update_layout(
        template="plotly_white",
        margin=dict(t=40, b=0, l=0, r=0),
        font=dict(family="Inter"),
        yaxis_title=None,
        xaxis_title=None
    )
    return fig

def plot_treemap(df, path, values, title):
    """Generates a Treemap."""
    fig = px.treemap(
        df, 
        path=path, 
        values=values,
        title=title,
        color_discrete_sequence=px.colors.qualitative.Prism
    )
    fig.update_layout(margin=dict(t=30, b=0, l=0, r=0))
    return fig
