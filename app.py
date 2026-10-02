import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Configuração da Página
st.set_page_config(page_title="Dashboard de Vendas", layout="wide", initial_sidebar_state="expanded")

# 2. Carregamento de Dados com Cache para Performance
@st.cache_data
def load_data():
    df = pd.read_csv('vendas_consolidado_limpo.csv')
    return df

df = load_data()

# 3. Configuração da Barra Lateral (Sidebar)
st.sidebar.header("⚙️ Filtros do Painel")

# Filtros Dinâmicos
anos_disponiveis = df['Ano'].dropna().unique().tolist()
ano_selecionado = st.sidebar.multiselect("Selecione o Ano", options=anos_disponiveis, default=anos_disponiveis)

status_disponiveis = df['Status'].dropna().unique().tolist()
status_selecionado = st.sidebar.multiselect("Status da Venda", options=status_disponiveis, default=["Concluída"])

regioes_disponiveis = df['Regiao'].dropna().unique().tolist()
regiao_selecionada = st.sidebar.multiselect("Região", options=regioes_disponiveis, default=regioes_disponiveis)

# Aplicação dos Filtros no DataFrame
df_filtrado = df[
    (df['Ano'].isin(ano_selecionado)) & 
    (df['Status'].isin(status_selecionado)) & 
    (df['Regiao'].isin(regiao_selecionada))
]

# 4. Cálculo dos KPIs Executivos
receita_total = df_filtrado['Valor_Total'].sum()
lucro_total = df_filtrado['Lucro_Estimado_R$'].sum()
qtd_transacoes = len(df_filtrado)
ticket_medio = receita_total / qtd_transacoes if qtd_transacoes > 0 else 0

# 5. Interface Principal - Cabeçalho e KPIs
st.title("📊 Painel Executivo de Vendas e Rentabilidade")
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Receita Total (Filtro)", f"R$ {receita_total:,.2f}")
col2.metric("Lucro Estimado", f"R$ {lucro_total:,.2f}")
col3.metric("Volume de Transações", f"{qtd_transacoes}")
col4.metric("Ticket Médio", f"R$ {ticket_medio:,.2f}")
st.markdown("---")

# 6. Gráficos e Memórias de Cálculo
col_grafico1, col_grafico2 = st.columns(2)

with col_grafico1:
    st.subheader("Receita por Categoria")
    
    # Prepara dados e plota
    df_categoria = df_filtrado.groupby('Categoria')['Valor_Total'].sum().reset_index().sort_values(by='Valor_Total', ascending=False)
    fig_cat = px.bar(df_categoria, x='Categoria', y='Valor_Total', text_auto='.2s', color='Categoria')
    fig_cat.update_traces(textposition='outside')
    st.plotly_chart(fig_cat, use_container_width=True)
    
    # Expander de Memória de Cálculo
    with st.expander("📚 Memória de Cálculo - Receita por Categoria"):
        st.markdown("""
        **Regra de Negócio:** Soma da coluna `Valor_Total` agrupada pela coluna de dimensão `Categoria`, respeitando os filtros de Ano, Status e Região ativos na barra lateral.
        
        **SQL:**
        ```sql
        SELECT Categoria, SUM(Valor_Total) AS Receita_Total 
        FROM vendas_consolidado 
        WHERE Status IN ('Concluída') AND Ano IN (2023, 2024) 
        GROUP BY Categoria
        ORDER BY Receita_Total DESC;
        ```
        
        **DAX (Power BI):**
        ```dax
        Receita_Por_Categoria = 
        CALCULATE(
            SUM(Vendas[Valor_Total]),
            KEEPFILTERS(Vendas[Status] = "Concluída")
        )
        ```
        
        **Excel:**
        ```excel
        =SOMASES(Vendas!Valor_Total; Vendas!Categoria; "Nome da Categoria"; Vendas!Status; "Concluída")
        ```
        """)

with col_grafico2:
    st.subheader("Evolução Mensal da Receita")
    
    # Prepara dados e plota
    df_mes = df_filtrado.groupby('Ano_Mes')['Valor_Total'].sum().reset_index().sort_values('Ano_Mes')
    fig_mes = px.line(df_mes, x='Ano_Mes', y='Valor_Total', markers=True)
    st.plotly_chart(fig_mes, use_container_width=True)
    
    # Expander de Memória de Cálculo
    with st.expander("📚 Memória de Cálculo - Evolução Mensal"):
        st.markdown("""
        **Regra de Negócio:** Soma da coluna `Valor_Total` agrupada cronologicamente pela coluna `Ano_Mes` (formato YYYY-MM) gerada na etapa de tratamento de dados.
        
        **SQL:**
        ```sql
        SELECT Ano_Mes, SUM(Valor_Total) AS Receita_Mensal 
        FROM vendas_consolidado 
        WHERE Status IN ('Concluída') 
        GROUP BY Ano_Mes 
        ORDER BY Ano_Mes ASC;
        ```
        
        **DAX (Power BI):**
        ```dax
        Receita_Evolucao = 
        CALCULATE(
            SUM(Vendas[Valor_Total]),
            USERELATIONSHIP(Vendas[Data_Venda], Calendario[Data])
        )
        ```
        
        **Excel:**
        ```excel
        =SOMASES(Vendas!Valor_Total; Vendas!Ano_Mes; "2024-01"; Vendas!Status; "Concluída")
        ```
        """)