import pandas as pd
import streamlit as st
from src.func import BalancoBanco as bb, Dados as dd, filtros as ft

st.title("Balanco das agencias")

# 1. Carrega os dados originais
df_original = dd.dados_transacoes()

# 2. Aplica o filtro de data primeiro e salva o resultado
df_filtrado_por_data = ft.filtrar_por_data(df_original)

# 3. Usa o DataFrame já filtrado por data como entrada para a função de filtro de agências
df_final = ft.filtrar_df_por_agencia_e_data(df_filtrado_por_data)

tab1, tab2, tab3, tab4 = st.tabs(["Tabela de Dados", "Gráfico de Transações", "Gráfico de Crescimento", "Gráfico de Transações"])

# Verifique se o DataFrame final não está vazio antes de gerar os gráficos
if not df_final.empty:
    with tab1:
        balanco_df = bb.balanco_data(df_final)
        st.dataframe(balanco_df)

    with tab2:
        balanco_df_para_grafico = balanco_df.reset_index()
        st.bar_chart(balanco_df_para_grafico.set_index('nome')[['total_saques', 'total_depositos']])

    with tab3:
        balanco_crescimento_df = bb.estatistica_data(df_final).reset_index()
        balanco_crescimento_df = balanco_crescimento_df.pivot(
            index='data_transacao',
            columns='nome',
            values='arrecadacao_total'
        )
        st.line_chart(balanco_crescimento_df)

    with tab4:
        balanco_transacoes_df = bb.transacoes_data(df_final).reset_index()
        balanco_transacoes_df = balanco_transacoes_df.pivot(
            index='data_transacao',
            columns='nome',
            values='num_transacoes'
        )
        st.line_chart(balanco_transacoes_df)
else:
    st.warning('Nenhum dado para exibir. Por favor, selecione uma agência.')