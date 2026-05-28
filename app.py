import streamlit as st
import pandas as pd
from datetime import date
from data import TICKERS, COLORS, get_stock_data, get_kpis
from charts import candlestick_chart, line_chart, performance_chart, heatmap_chart

st.set_page_config(
    page_title="Ações B3 — Análise 2025",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Dashboard de Ações B3 — 2025")
st.caption("Petrobrás (PETR4) · Itaú (ITUB4) · Vale (VALE3)")

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Configurações")

    acoes_selecionadas = st.multiselect(
        "Ações para exibir",
        options=list(TICKERS.keys()),
        default=list(TICKERS.keys()),
    )

    col1, col2 = st.columns(2)
    data_inicio = col1.date_input("Início", value=date(2025, 1, 2), min_value=date(2025, 1, 2), max_value=date(2025, 12, 31))
    data_fim = col2.date_input("Fim", value=date(2025, 12, 31), min_value=date(2025, 1, 2), max_value=date(2025, 12, 31))

    tipo_grafico = st.radio("Tipo de gráfico principal", ["Candlestick", "Linha"])
    mostrar_tabela = st.checkbox("Mostrar tabela de dados", value=False)

if not acoes_selecionadas:
    st.warning("Selecione ao menos uma ação na sidebar.")
    st.stop()

# ── Busca de dados ────────────────────────────────────────────────────────────
dados = {}
for nome in acoes_selecionadas:
    ticker = TICKERS[nome]
    df = get_stock_data(ticker, str(data_inicio), str(data_fim))
    dados[nome] = (df, COLORS[nome])

# ── KPIs ──────────────────────────────────────────────────────────────────────
st.subheader("Resumo do período selecionado")
kpi_cols = st.columns(len(acoes_selecionadas))

for i, nome in enumerate(acoes_selecionadas):
    df, cor = dados[nome]
    kpis = get_kpis(df)
    with kpi_cols[i]:
        st.markdown(f"**{nome}**")
        if kpis:
            retorno = kpis["retorno_total"]
            variacao = kpis["variacao_diaria"]
            st.metric("Cotação atual", f"R$ {kpis['cotacao_atual']:.2f}",
                      delta=f"{variacao:+.2f}% hoje")
            st.metric("Retorno no período", f"{retorno:+.2f}%")
            st.metric("Máxima / Mínima", f"R$ {kpis['max_periodo']:.2f} / R$ {kpis['min_periodo']:.2f}")
            st.metric("Volume médio diário", f"{kpis['volume_medio']:,.0f}")
        else:
            st.warning("Sem dados")

st.divider()

# ── Gráfico principal por ação ────────────────────────────────────────────────
st.subheader("Cotação Individual")

for nome in acoes_selecionadas:
    df, cor = dados[nome]
    if df.empty:
        st.warning(f"Sem dados para {nome} no período selecionado.")
        continue
    if tipo_grafico == "Candlestick":
        fig = candlestick_chart(df, nome, cor)
    else:
        fig = line_chart(df, nome, cor)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── Performance comparativa ───────────────────────────────────────────────────
st.subheader("Performance Comparativa")
fig_perf = performance_chart(dados)
st.plotly_chart(fig_perf, use_container_width=True)

st.divider()

# ── Mapa de calor mensal ──────────────────────────────────────────────────────
st.subheader("Retorno Mensal por Ação")
# Para o heatmap usamos sempre o ano completo de 2025 para contexto
dados_2025 = {}
for nome in acoes_selecionadas:
    ticker = TICKERS[nome]
    df_anual = get_stock_data(ticker, "2025-01-02", "2025-12-31")
    dados_2025[nome] = (df_anual, COLORS[nome])

fig_heat = heatmap_chart(dados_2025)
st.plotly_chart(fig_heat, use_container_width=True)

# ── Tabela de dados brutos ────────────────────────────────────────────────────
if mostrar_tabela:
    st.divider()
    st.subheader("Dados Brutos")
    for nome in acoes_selecionadas:
        df, _ = dados[nome]
        if not df.empty:
            with st.expander(f"Tabela — {nome}"):
                exibir = df[["Open", "High", "Low", "Close", "Volume", "MM20", "MM50", "Retorno_Acumulado", "Variacao_Diaria"]].copy()
                exibir.index = exibir.index.strftime("%d/%m/%Y")
                exibir.columns = ["Abertura", "Máxima", "Mínima", "Fechamento", "Volume", "MM20", "MM50", "Retorno Acum. (%)", "Var. Diária (%)"]
                st.dataframe(exibir.style.format({
                    "Abertura": "R$ {:.2f}", "Máxima": "R$ {:.2f}",
                    "Mínima": "R$ {:.2f}", "Fechamento": "R$ {:.2f}",
                    "Volume": "{:,.0f}", "MM20": "R$ {:.2f}", "MM50": "R$ {:.2f}",
                    "Retorno Acum. (%)": "{:+.2f}%", "Var. Diária (%)": "{:+.2f}%",
                }), use_container_width=True)

st.caption("Dados: Yahoo Finance via yfinance · Atualizado a cada hora")
