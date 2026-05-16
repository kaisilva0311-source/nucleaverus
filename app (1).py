import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import time

# Configuração da Página
st.set_page_config(
    page_title="NÚCLEA Verus | Cockpit de Compliance",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Estilização Dark Mode Customizada
st.markdown("""
    <style>
    .main {
        background-color: #0E1117;
    }
    .stMetric {
        background-color: #1E2130;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #31333F;
    }
    .stDataFrame {
        border: 1px solid #31333F;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# Header
st.title("🛡️ NÚCLEA Verus | Cockpit de Compliance CVM 175")
st.markdown("---")

# Linha de KPIs
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Status de Compliance", value="✅ CONFORME", delta=None)

with col2:
    # Patrimônio Líquido com variação negativa
    st.metric(
        label="Patrimônio Líquido", 
        value="R$ 504.230.000", 
        delta="-0.5% (Ajuste MtM)",
        delta_color="inverse"
    )

with col3:
    st.metric(label="Conexão NÚCLEA", value="📡 ONLINE (D-0)", delta="Estável", delta_color="normal")

st.markdown("<br>", unsafe_allow_html=True)

# Geração de Dados Simulados (DataFrame)
@st.cache_data
def get_data():
    data = {
        "ID Ativo": ["FIDC-044", "FIDC-102", "FIDC-089", "FIDC-211", "FIDC-156"],
        "Valor de Face": [1250000.00, 850000.00, 2100000.00, 450000.00, 980000.00],
        "Score": [98, 85, 92, 45, 88],
        "Status NÚCLEA": ["Pago", "A Vencer", "A Vencer", "Atrasado", "Pago"],
        "Preço Justo (Calculado)": [1250000.00, 848500.00, 2095000.00, 410000.00, 980000.00],
        "Ação Recomendada": ["Manter", "Monitorar", "Manter", "Provisionar", "Manter"]
    }
    return pd.DataFrame(data)

df = get_data()

# Corpo Principal (2 colunas - 70/30)
body_col1, body_col2 = st.columns([7, 3])

with body_col1:
    st.subheader("📋 Carteira de Ativos de Crédito")
    st.dataframe(
        df, 
        use_container_width=True,
        column_config={
            "Valor de Face": st.column_config.NumberColumn(format="R$ %.2f"),
            "Preço Justo (Calculado)": st.column_config.NumberColumn(format="R$ %.2f"),
            "Score": st.column_config.ProgressColumn(min_value=0, max_value=100)
        }
    )

with body_col2:
    st.subheader("⚡ Feed ao Vivo (Kafka)")
    # Container simulando log em tempo real
    with st.container(height=300, border=True):
        logs = [
            f"⚡ {datetime.now().strftime('%H:%M:%S')} - Conexão estabelecida com cluster Kafka",
            f"⚡ {datetime.now().strftime('%H:%M:%S')} - Ativo FIDC-044 pago integralmente",
            f"⚡ {datetime.now().strftime('%H:%M:%S')} - Alerta: FIDC-211 apresenta atraso > 5 dias",
            f"⚡ {datetime.now().strftime('%H:%M:%S')} - Re-calculando Preço Justo via motor Verus",
            f"⚡ {datetime.now().strftime('%H:%M:%S')} - Compliance CVM 175 validado com sucesso",
            f"⚡ {datetime.now().strftime('%H:%M:%S')} - Novo lote de recebíveis processado (n=142)"
        ]
        for log in reversed(logs):
            st.code(log, language="bash")

st.markdown("---")

# Drill-Down (Gráfico)
st.subheader("📈 Análise de Ativo Selecionado (Drill-Down)")

selected_id = st.selectbox("Selecione o Ativo para Visualização:", df["ID Ativo"])

# Simulação de dados temporais para o gráfico
def get_time_series_data(asset_id):
    # Pega o valor de face do dataframe original
    face_value = df[df["ID Ativo"] == asset_id]["Valor de Face"].values[0]
    status = df[df["ID Ativo"] == asset_id]["Status NÚCLEA"].values[0]
    
    dates = pd.date_range(start="2024-01-01", periods=10, freq="D")
    
    # Valor de Face é uma linha reta
    face_values = [face_value] * 10
    
    # Valor Marcado a Mercado (MtM)
    # Se estiver atrasado, simula uma queda no final
    mtm_values = [face_value] * 8
    if status == "Atrasado":
        mtm_values.extend([face_value * 0.95, face_value * 0.90])
    else:
        mtm_values.extend([face_value, face_value])
        
    return pd.DataFrame({
        "Data": dates,
        "Valor de Face": face_values,
        "Valor Marcado a Mercado": mtm_values
    })

chart_data = get_time_series_data(selected_id)

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=chart_data["Data"], 
    y=chart_data["Valor de Face"],
    mode='lines',
    name='Valor de Face',
    line=dict(color='#00FFAA', width=2, dash='dash')
))

fig.add_trace(go.Scatter(
    x=chart_data["Data"], 
    y=chart_data["Valor Marcado a Mercado"],
    mode='lines+markers',
    name='Valor Marcado a Mercado (MtM)',
    line=dict(color='#FF4B4B', width=3)
))

fig.update_layout(
    template="plotly_dark",
    xaxis_title="Período de Monitoramento",
    yaxis_title="Valor (R$)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    margin=dict(l=0, r=0, t=30, b=0),
    height=400
)

st.plotly_chart(fig, use_container_width=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.caption("NÚCLEA Verus v1.0.4 | Desenvolvido por Engenharia de Dados Sênior | © 2026")
