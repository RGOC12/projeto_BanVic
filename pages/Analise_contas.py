import streamlit as st
import pandas as pd
import plotly.express as px
from src.func import dados as dd, contas_bancarias as cb, filtros as ft

# 1. Carregar todos os dados de forma eficiente
propostas_df, contas_df, transacoes_df, clientes_df = dd.dados_para_analise()
agencias_df = pd.read_csv("src/data/agencias.csv")
colaborador_agencia_df = pd.read_csv("src/data/colaborador_agencia.csv")

propostas_df['data_entrada_proposta'] = pd.to_datetime(propostas_df['data_entrada_proposta'], format='mixed', errors='coerce').dt.tz_localize(None)
contas_df['data_abertura'] = pd.to_datetime(contas_df['data_abertura'], format='mixed', errors='coerce').dt.tz_localize(None)
contas_df['data_ultimo_lancamento'] = pd.to_datetime(contas_df['data_ultimo_lancamento'], format='mixed', errors='coerce').dt.tz_localize(None)
transacoes_df['data_transacao'] = pd.to_datetime(transacoes_df['data_transacao'], format='mixed', errors='coerce').dt.tz_localize(None)

propostas_df = pd.merge(propostas_df, colaborador_agencia_df, on='cod_colaborador', how='left')
propostas_df = pd.merge(propostas_df, agencias_df[['cod_agencia', 'nome']], on='cod_agencia', how='left')
transacoes_df = pd.merge(transacoes_df, contas_df[['num_conta', 'cod_agencia']], on='num_conta', how='left')
transacoes_df = pd.merge(transacoes_df, agencias_df[['cod_agencia', 'nome']], on='cod_agencia', how='left')

total_clientes = clientes_df.shape[0]

# --- Seção de Filtros no Streamlit ---
st.sidebar.header("Filtros")

min_data = propostas_df['data_entrada_proposta'].min().date()
max_data = propostas_df['data_entrada_proposta'].max().date()
data_inicio = st.sidebar.date_input("Data de Início", min_value=min_data, max_value=max_data, value=min_data)
data_fim = st.sidebar.date_input("Data de Fim", min_value=min_data, max_value=max_data, value=max_data)

if data_inicio > data_fim:
    st.sidebar.warning("⚠️ A data inicial é maior que a final.")
    data_inicio, data_fim = data_fim, data_inicio

todas_agencias = agencias_df['nome'].unique()
agencias_selecionadas = st.sidebar.multiselect(
    'Selecione as Agências:',
    options=todas_agencias,
    default=todas_agencias
)

# Aplicar o filtro de data em ambos os DataFrames
propostas_filtradas = ft.filtrar_por_data_cliente(propostas_df, data_inicio, data_fim, "data_entrada_proposta")
transacoes_filtradas = ft.filtrar_por_data_cliente(transacoes_df, data_inicio, data_fim, "data_transacao")

# Aplicar o filtro de agência
if agencias_selecionadas:
    propostas_filtradas = ft.filtrar_df_por_agencia(propostas_filtradas, agencias_selecionadas)
    transacoes_filtradas = ft.filtrar_df_por_agencia(transacoes_filtradas, agencias_selecionadas)
else:
    propostas_filtradas = propostas_df[propostas_df['nome'].isin(agencias_selecionadas)]
    transacoes_filtradas = transacoes_df[transacoes_df['nome'].isin(agencias_selecionadas)]

# 2. Realizar a análise com os DataFrames FILTRADOS
analise = cb.transacoes_contas(propostas_filtradas, transacoes_filtradas, contas_df, clientes_df)
df_analise_final = analise['df_analise']

# 3. Gerar a nova tabela de clientes sem proposta (lógica fixada para 2022)
propostas_2022 = propostas_df[propostas_df['data_entrada_proposta'].dt.year == 2022]
df_sem_proposta = cb.clientes_sem_proposta(
    propostas_2022, clientes_df, contas_df, agencias_df
)

st.header("Análise de Clientes: Transações vs. Propostas")
st.markdown("...")

tabela_tab, grafico_tab, clientes_sem_proposta_tab = st.tabs(["Tabela de Dados", "Gráfico de Análise", "Clientes que Não Receberam Propostas de Crédito"])

with tabela_tab:
    st.subheader("Tabela de Dados Agregados")
    st.dataframe(df_analise_final)

with grafico_tab:
    st.subheader("Gráfico de Análise")
    colunas_para_derreter = ['Aprovada', 'Rejeitada', 'Em Análise', 'Enviada', 'Validação documentos', 'Saque', 'Depósito']
    colunas_presentes = [col for col in colunas_para_derreter if col in df_analise_final.columns]
    
    # ⚠️ Alteração: Agora usa a coluna 'nome_completo' no gráfico
    df_longo = pd.melt(df_analise_final, id_vars=['nome_completo'], value_vars=colunas_presentes, var_name='Tipo de Análise', value_name='Quantidade/Valor')

    fig = px.bar(
        df_longo,
        x='nome_completo',
        y='Quantidade/Valor',
        color='Tipo de Análise',
        title='Status de Propostas e Transações por Cliente',
        labels={'nome_completo': 'Nome do Cliente', 'Quantidade/Valor': 'Nº de Propostas / Valor de Transações'}
    )
    fig.update_layout(xaxis_title="Nome do Cliente", yaxis_title="Nº de Propostas / Valor de Transações", legend_title="Tipo de Análise")
    st.plotly_chart(fig, use_container_width=True)

with clientes_sem_proposta_tab:
    st.subheader("Clientes que Não Receberam Propostas de Crédito em 2022")
    st.dataframe(df_sem_proposta)