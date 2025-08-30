import pandas as pd
import streamlit as st
from src.func import AnaliseBanco as ab, dados_transacoes

st.title("Balanco das agencias")

df_original = dados_transacoes()
df_original['data_transacao'] = pd.to_datetime(df_original['data_transacao']).dt.tz_localize(None)

min_data = df_original['data_transacao'].min().date()
max_data = df_original['data_transacao'].max().date()

st.sidebar.header("Filtros")
data_inicio = st.sidebar.date_input("Data de Início", min_value=min_data, max_value=max_data, value=min_data)
data_fim = st.sidebar.date_input("Data de Fim", min_value=min_data, max_value=max_data, value=max_data)

if data_inicio > data_fim:
    st.warning("⚠️ A data inicial é maior que a final.")
    data_inicio, data_fim = data_fim, data_inicio

df_filtrado_por_data = df_original[
    (df_original['data_transacao'] >= pd.to_datetime(data_inicio)) &
    (df_original['data_transacao'] <= pd.to_datetime(data_fim))
]
tab1, tab2, tab3, tab4 = st.tabs(["Tabela de Dados", "Gráfico de Transações","Gráfico de Crescimento","Gráfico de Transações"])

with tab1:
    balanco_df = ab.balanco_data(df_filtrado_por_data)
    st.dataframe(balanco_df)

with tab2:
    balanco_df_para_grafico = balanco_df.reset_index()
    st.bar_chart(balanco_df_para_grafico.set_index('nome')[['total_saques', 'total_depositos']])

with tab3:
    balanco_crescimento_df = ab.estatistica_data(df_filtrado_por_data).reset_index()
    balanco_crescimento_df = balanco_crescimento_df.pivot(
        index='data_transacao', 
        columns='nome', 
        values='arrecadacao_total'
    )
    st.line_chart(balanco_crescimento_df)

with tab4:
    balanco_transacoes_df = ab.transacoes_data(df_filtrado_por_data).reset_index()
    print(balanco_transacoes_df)
    balanco_transacoes_df = balanco_transacoes_df.pivot(
        index= 'data_transacao', 
        columns='nome', 
        values= 'num_transacoes'
    )
    st.line_chart(balanco_transacoes_df)