import pandas as pd
import streamlit as st
import numpy as np

@st.cache_data
def dados_transacoes():
    agencias_df = pd.read_csv('agencias.csv')
    transacoes_df = pd.read_csv('transacoes.csv')
    contas_df = pd.read_csv('contas.csv')
    transacoes_df['data_transacao'] = pd.to_datetime(
        transacoes_df['data_transacao'], format='mixed', utc=True
    )
    transacoes_df['data_transacao'] = transacoes_df['data_transacao'].dt.tz_localize(None)
    capital_agencia_df = pd.merge( contas_df,transacoes_df, on='num_conta', how='left')
    capital_agencia_df = pd.merge( capital_agencia_df,agencias_df, on='cod_agencia', how='left')
    capital_agencia_df.rename(columns={'data_abertura_y': 'data_abertura'}, inplace=True)
    return capital_agencia_df

def maiores_saques(saques):
    saques_df = saques
    saques_df['depositos'] = np.where(saques_df['valor_transacao'] > 0, saques_df['valor_transacao'], 0)
    saques_df['saques'] = np.where(saques_df['valor_transacao'] < 0, saques_df['valor_transacao'], 0)
    saques_df['arrecadacao_total'] = saques_df['depositos'] + saques_df['saques']
    saques_df = saques_df.groupby(['data_abertura','nome', 'uf','tipo_agencia']).agg(num_transacoes=('num_conta', 'count'),total_saques=('saques','sum'),total_depositos=('depositos','sum'), arrecadacao_total = ('arrecadacao_total','sum'))
    return saques_df

st.set_page_config(page_title="Banco VICTOR", layout="wide")
st.title("Análise de Dados - Banco VICTOR")

df_original = dados_transacoes()
print(df_original.dtypes)
df_original['data_transacao'] = pd.to_datetime(df_original['data_transacao']).dt.tz_localize(None)


min_data = df_original['data_transacao'].min().date()
max_data = df_original['data_transacao'].max().date()

# Inputs com limites
data_inicio = st.date_input("Data de Início", min_value=min_data, max_value=max_data, value=min_data)
data_fim = st.date_input("Data de Fim", min_value=min_data, max_value=max_data, value=max_data)

# Corrigir se as datas forem invertidas
if data_inicio > data_fim:
    st.warning("⚠️ A data inicial é maior que a final.")
    data_inicio, data_fim = data_fim, data_inicio

# Filtrar por intervalo
df_filtrado_por_data = df_original[
    (df_original['data_transacao'] >= pd.to_datetime(data_inicio)) &
    (df_original['data_transacao'] <= pd.to_datetime(data_fim))
]

saques_df = maiores_saques(df_filtrado_por_data)
st.dataframe(saques_df)


saques_df_para_grafico = saques_df.reset_index()
st.bar_chart(saques_df_para_grafico.set_index('nome')[['total_saques', 'total_depositos']])