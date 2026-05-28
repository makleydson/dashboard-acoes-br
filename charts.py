import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd


def candlestick_chart(df: pd.DataFrame, nome: str, cor: str) -> go.Figure:
    fig = make_subplots(
        rows=2, cols=1, shared_xaxes=True,
        row_heights=[0.75, 0.25], vertical_spacing=0.03,
    )
    fig.add_trace(
        go.Candlestick(
            x=df.index, open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            name=nome, increasing_line_color="#26A69A", decreasing_line_color="#EF5350",
        ),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MM20"], name="MM20", line=dict(color="orange", width=1.5)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Scatter(x=df.index, y=df["MM50"], name="MM50", line=dict(color="purple", width=1.5)),
        row=1, col=1,
    )
    fig.add_trace(
        go.Bar(x=df.index, y=df["Volume"], name="Volume", marker_color=cor, opacity=0.6),
        row=2, col=1,
    )
    fig.update_layout(
        title=f"Cotação {nome} — Candlestick com Médias Móveis",
        xaxis_rangeslider_visible=False,
        template="plotly_dark",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    fig.update_yaxes(title_text="Preço (R$)", row=1, col=1)
    fig.update_yaxes(title_text="Volume", row=2, col=1)
    return fig


def line_chart(df: pd.DataFrame, nome: str, cor: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df["Close"], name="Fechamento",
        line=dict(color=cor, width=2),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MM20"], name="MM20",
        line=dict(color="orange", width=1.5, dash="dot"),
    ))
    fig.add_trace(go.Scatter(
        x=df.index, y=df["MM50"], name="MM50",
        line=dict(color="purple", width=1.5, dash="dot"),
    ))
    fig.update_layout(
        title=f"Cotação {nome} — Linha com Médias Móveis",
        template="plotly_dark", height=400,
        yaxis_title="Preço (R$)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def performance_chart(dados: dict) -> go.Figure:
    fig = go.Figure()
    for nome, (df, cor) in dados.items():
        if not df.empty:
            fig.add_trace(go.Scatter(
                x=df.index, y=df["Retorno_Acumulado"],
                name=nome, line=dict(color=cor, width=2),
            ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(
        title="Performance Comparativa — Retorno Acumulado 2025 (%)",
        template="plotly_dark", height=400,
        yaxis_title="Retorno Acumulado (%)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def heatmap_chart(dados: dict) -> go.Figure:
    meses_pt = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
                 "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    rows, labels = [], []
    for nome, (df, _) in dados.items():
        if df.empty:
            continue
        monthly = df["Close"].resample("ME").last().pct_change() * 100
        monthly = monthly.dropna()
        row = []
        for m in range(1, 13):
            vals = monthly[monthly.index.month == m]
            row.append(round(vals.iloc[0], 2) if not vals.empty else None)
        rows.append(row)
        labels.append(nome)

    if not rows:
        return go.Figure()

    fig = go.Figure(data=go.Heatmap(
        z=rows,
        x=meses_pt,
        y=labels,
        colorscale=[
            [0.0, "#D32F2F"], [0.4, "#EF9A9A"],
            [0.5, "#F5F5F5"],
            [0.6, "#A5D6A7"], [1.0, "#1B5E20"],
        ],
        zmid=0,
        text=[[f"{v:.1f}%" if v is not None else "N/D" for v in row] for row in rows],
        texttemplate="%{text}",
        hovertemplate="Ação: %{y}<br>Mês: %{x}<br>Retorno: %{text}<extra></extra>",
        colorbar=dict(title="Retorno (%)"),
    ))
    fig.update_layout(
        title="Mapa de Calor — Retorno Mensal 2025 (%)",
        template="plotly_dark", height=300,
    )
    return fig
