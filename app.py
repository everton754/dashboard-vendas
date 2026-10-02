import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. Configuração da Página
st.set_page_config(
    page_title="Painel Comercial de Vendas",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Injeção de CSS para recriar a interface SaaS Dark Mode do Artefato
st.markdown("""
<style>
    /* Estilo Geral do Fundo */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Sidebar Escura e Estilizada */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Cards de KPI Executivos estilo Power BI / SaaS */
    .kpi-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 12px;
    }
    .kpi-title {
        color: #8b949e;
        font-size: 0.82rem;
        font-weight: 500;
        margin-bottom: 4px;
        display: flex;
        justify-content: space-between;
    }
    .kpi-value {
        color: #f0f6fc;
        font-size: 1.65rem;
        font-weight: 700;
        letter-spacing: -0.02em;
    }
    .kpi-sub {
        color: #58a6ff;
        font-size: 0.75rem;
        margin-top: 4px;
    }

    /* Borda e Fundo dos Gráficos em Containers */
    [data-testid="stVerticalBlock"] > div > div[data-testid="stVerticalBlock"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 12px;
    }

    /* Estilização das Abas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: #161b22;
        border-radius: 6px;
        color: #8b949e;
        font-size: 0.88rem;
        border: 1px solid #30363d;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        color: #f0f6fc !important;
        border-color: #58a6ff !important;
    }
    
    /* Titulos e Cabeçalhos */
    h1, h2, h3 {
        color: #f0f6fc !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. Cache de Dados
@st.cache_data
def load_data():
    df = pd.read_csv('vendas_consolidado_limpo.csv')
    df['Data_Venda'] = pd.to_datetime(df['Data_Venda'])
    df['Ano_Mes'] = df['Data_Venda'].dt.to_period('M').astype(str)
    return df

df = load_data()

# 4. Sidebar - Filtros
st.sidebar.header("⚙️ Filtros do Painel")
st.sidebar.markdown("---")

anos_disponiveis = sorted(df['Ano'].dropna().unique().tolist())
ano_selecionado = st.sidebar.multiselect("📅 Selecione o Ano", options=anos_disponiveis, default=anos_disponiveis)

regioes_disponiveis = sorted(df['Regiao'].dropna().unique().tolist())
regiao_selecionada = st.sidebar.multiselect("🌍 Região", options=regioes_disponiveis, default=regioes_disponiveis)

canais_disponiveis = sorted(df['Canal_Venda'].dropna().unique().tolist())
canal_selecionado = st.sidebar.multiselect("🛒 Canal de Venda", options=canais_disponiveis, default=canais_disponiveis)

status_disponiveis = sorted(df['Status'].dropna().unique().tolist())
# REGRA DE NEGÓCIO: Iniciar apenas com 'Concluída' evita distorção da receita real no topo
status_selecionado = st.sidebar.multiselect("✅ Status", options=status_disponiveis, default=["Concluída"])

# Filtragem do Dataframe
df_filtrado = df[
    (df['Ano'].isin(ano_selecionado)) &
    (df['Regiao'].isin(regiao_selecionada)) &
    (df['Canal_Venda'].isin(canal_selecionado)) &
    (df['Status'].isin(status_selecionado))
]

# 5. Cálculos dos KPIs
receita_total = df_filtrado['Valor_Total'].sum()
qtd_vendas = len(df_filtrado)
ticket_medio = receita_total / qtd_vendas if qtd_vendas > 0 else 0
qtd_itens = df_filtrado['Quantidade'].sum()
vendas_concluidas = len(df_filtrado[df_filtrado['Status'] == 'Concluída'])
taxa_conclusao = (vendas_concluidas / qtd_vendas * 100) if qtd_vendas > 0 else 0
vendas_canceladas = len(df_filtrado[df_filtrado['Status'] == 'Cancelada'])
taxa_cancelamento = (vendas_canceladas / qtd_vendas * 100) if qtd_vendas > 0 else 0
lucro_total = df_filtrado['Lucro_Estimado_R$'].sum()

# Função para aplicar tema escuro elegante em todos os gráficos do Plotly
def aplicar_tema_escuro(fig, titulo=""):
    fig.update_layout(
        title=dict(text=titulo, font=dict(color='#f0f6fc', size=14)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=15, r=15, t=35, b=15),
        font=dict(color='#8b949e', family="Inter, sans-serif"),
        xaxis=dict(showgrid=True, gridcolor='#21262d', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#21262d', zeroline=False),
        legend=dict(font=dict(color='#c9d1d9'))
    )
    return fig

# Cabeçalho Principal
st.title("📊 Painel Executivo de Vendas e Rentabilidade")
st.markdown("---")

# Cards de KPI no Topo em Containers Estilizados
c1, c2, c3, c4, c5 = st.columns(5)

c1.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">Receita Total <span>ℹ️</span></div>
    <div class="kpi-value">R$ {receita_total:,.0f}</div>
    <div class="kpi-sub">{qtd_vendas} vendas</div>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">Lucro Estimado <span>ℹ️</span></div>
    <div class="kpi-value">R$ {lucro_total:,.0f}</div>
    <div class="kpi-sub">Margem média</div>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">Ticket Médio <span>ℹ️</span></div>
    <div class="kpi-value">R$ {ticket_medio:,.0f}</div>
    <div class="kpi-sub">por transação</div>
</div>
""", unsafe_allow_html=True)

c4.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">Itens Vendidos <span>ℹ️</span></div>
    <div class="kpi-value">{qtd_itens:,.0f}</div>
    <div class="kpi-sub">unidades</div>
</div>
""", unsafe_allow_html=True)

c5.markdown(f"""
<div class="kpi-card">
    <div class="kpi-title">Taxa Conclusão <span>ℹ️</span></div>
    <div class="kpi-value">{taxa_conclusao:.1f}%</div>
    <div class="kpi-sub">{vendas_concluidas} concluídas</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Estrutura de Abas
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Visão Geral", 
    "👥 Vendedores & Metas", 
    "📦 Produtos & Clientes",
    "🗺️ Geográfico",
    "📋 Dados Detalhados"
])

# ABA 1: VISÃO GERAL
with tab1:
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        df_mes = df_filtrado.groupby('Ano_Mes')['Valor_Total'].sum().reset_index()
        fig_mes = px.line(df_mes, x='Ano_Mes', y='Valor_Total', markers=True)
        fig_mes.update_traces(line_color='#d97706', line_width=3, marker=dict(size=6, color='#f59e0b'))
        fig_mes = aplicar_tema_escuro(fig_mes, "Evolução Mensal da Receita")
        st.plotly_chart(fig_mes, use_container_width=True)
        
        with st.expander("ℹ️ Memória de Cálculo - Evolução Mensal"):
            st.markdown("""
            **Regra de Negócio:** Soma de `Valor_Total` por Mês/Ano.
            ```sql
            SELECT Ano_Mes, SUM(Valor_Total) FROM vendas_consolidado GROUP BY Ano_Mes;
            ```
            """)
    
    with col_g2:
        df_cat = df_filtrado.groupby('Categoria')['Valor_Total'].sum().reset_index()
        fig_cat = px.pie(
            df_cat, values='Valor_Total', names='Categoria', hole=0.6,
            color_discrete_sequence=['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6']
        )
        fig_cat = aplicar_tema_escuro(fig_cat, "Participação por Categoria")
        st.plotly_chart(fig_cat, use_container_width=True)
        
        with st.expander("ℹ️ Memória de Cálculo - Categoria"):
            st.markdown("""
            **Regra de Negócio:** Soma de `Valor_Total` por Categoria do Produto.
            ```sql
            SELECT Categoria, SUM(Valor_Total) FROM vendas_consolidado GROUP BY Categoria;
            ```
            """)

    col_g3, col_g4 = st.columns(2)
    
    with col_g3:
        df_status = df_filtrado.groupby('Status')['ID_Venda'].count().reset_index()
        fig_status = px.bar(
            df_status, x='Status', y='ID_Venda', color='Status',
            color_discrete_map={'Concluída': '#10b981', 'Pendente': '#f59e0b', 'Cancelada': '#ef4444', 'Em Processamento': '#3b82f6'}
        )
        fig_status = aplicar_tema_escuro(fig_status, "Distribuição por Status")
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col_g4:
        df_canal = df_filtrado.groupby('Canal_Venda')['Valor_Total'].sum().reset_index()
        fig_canal = px.bar(df_canal, x='Canal_Venda', y='Valor_Total', color_discrete_sequence=['#3b82f6'])
        fig_canal = aplicar_tema_escuro(fig_canal, "Faturamento por Canal")
        st.plotly_chart(fig_canal, use_container_width=True)

# ABA 2: VENDEDORES & METAS
with tab2:
    st.header("👥 Performance de Vendedores")
    
    num_meses = df_filtrado['Ano_Mes'].nunique()
    num_meses = num_meses if num_meses > 0 else 1
    
    df_meta = df_filtrado.groupby('Nome_Vendedor').agg({
        'Valor_Total': 'sum',
        'Meta_Mensal': 'first'
    }).reset_index()
    
    df_meta['Meta_Ajustada'] = df_meta['Meta_Mensal'] * num_meses
    df_meta['Atingimento_%'] = (df_meta['Valor_Total'] / df_meta['Meta_Ajustada'] * 100)
    df_meta = df_meta.sort_values('Atingimento_%', ascending=False)
    
    st.dataframe(
        df_meta[['Nome_Vendedor', 'Valor_Total', 'Meta_Ajustada', 'Atingimento_%']].style.format({
            'Valor_Total': 'R$ {:,.2f}',
            'Meta_Ajustada': 'R$ {:,.2f}',
            'Atingimento_%': '{:.1f}%'
        }),
        use_container_width=True,
        hide_index=True
    )

# ABA 3: PRODUTOS & CLIENTES
with tab3:
    st.header("📦 Análise de Produtos e Clientes")
    col_p1, col_p2 = st.columns(2)
    
    with col_p1:
        df_prod = df_filtrado.groupby('Produto')['Valor_Total'].sum().reset_index().sort_values('Valor_Total', ascending=True).tail(10)
        fig_prod = px.bar(df_prod, x='Valor_Total', y='Produto', orientation='h', color_discrete_sequence=['#10b981'])
        fig_prod = aplicar_tema_escuro(fig_prod, "Top 10 Produtos por Receita")
        st.plotly_chart(fig_prod, use_container_width=True)
        
    with col_p2:
        df_cli = df_filtrado.groupby(['Nome_Cliente', 'Segmento'])['Valor_Total'].sum().reset_index().sort_values('Valor_Total', ascending=True).tail(10)
        fig_cli = px.bar(df_cli, x='Valor_Total', y='Nome_Cliente', orientation='h', color='Segmento')
        fig_cli = aplicar_tema_escuro(fig_cli, "Top 10 Clientes")
        st.plotly_chart(fig_cli, use_container_width=True)

# ABA 4: GEOGRÁFICO
with tab4:
    st.header("🗺️ Análise Geográfica")
    df_uf = df_filtrado.groupby('UF')['Valor_Total'].sum().reset_index().sort_values('Valor_Total', ascending=False)
    fig_uf = px.bar(df_uf, x='UF', y='Valor_Total', color='Valor_Total', color_continuous_scale='Blues')
    fig_uf = aplicar_tema_escuro(fig_uf, "Faturamento por Estado (UF)")
    st.plotly_chart(fig_uf, use_container_width=True)

# ABA 5: DADOS DETALHADOS
with tab5:
    st.header("📋 Detalhamento das Vendas")
    st.dataframe(df_filtrado.head(300), use_container_width=True, hide_index=True)
    
    csv = df_filtrado.to_csv(index=False, sep=';', decimal=',')
    st.download_button(
        label="📥 Download dos Dados Filtrados (CSV)",
        data=csv,
        file_name=f"vendas_filtradas_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
