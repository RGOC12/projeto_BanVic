import pandas as pd
import streamlit as st
from src.func import BalancoBanco as bb, Dados as dd, filtros as ft, view as vw
import numpy as np


st.title("Balanco das agencias")

# 1. Carrega os dados originais
df_original = dd.dados_transacoes()
# 2. Aplica o filtro de data primeiro e salva o resultado
df_filtrado_por_data = ft.filtrar_por_data(df_original)

# 3. Usa o DataFrame já filtrado por data como entrada para a função de filtro de agências
df_final = ft.filtrar_df_por_agencia_e_data(df_filtrado_por_data)

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Tabela de Dados", "Gráfico de Transações", "Gráfico de Crescimento", "Gráfico de Transações", "grafico"])

# Verifique se o DataFrame final não está vazio antes de gerar os gráficos
if not df_final.empty:
    with tab1:
        balanco_df = bb.balanco_data(df_final)
        st.dataframe(balanco_df)
        #--------------------------------------------
        #--------------------------------------------
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

        st.header('Ranking de Agências por Número de Transações')

        # Executa a função de ranking que criamos
        ranking_df = bb.ranking_transacoes(df_final)

        # Exibe o ranking em uma tabela completa
        st.subheader('Ranking Completo')
        st.dataframe(ranking_df)
        
        # Exibe um gráfico de barras para facilitar a visualização
        st.bar_chart(ranking_df.set_index('nome'))

        # Exibe o resumo do ranking
        st.subheader('Resumo do Ranking')
        melhores_3 = ranking_df.head(3)
        piores_3 = ranking_df.tail(3)

        st.markdown(f"""
        **1. Agência com Maior Número de Transações:**
        * **{melhores_3['nome'].iloc[0]}** com **{melhores_3['total_transacoes'].iloc[0]}** transações.

        **2. Agência com Menor Número de Transações:**
        * **{piores_3['nome'].iloc[-1]}** com **{piores_3['total_transacoes'].iloc[-1]}** transações.

        **3. Top 3 Melhores Agências:**
        """)
        st.dataframe(melhores_3)
        
        st.markdown("""
        **4. Top 3 Piores Agências:**
        """)
        st.dataframe(piores_3)
        
        st.markdown("""
        **Justificativa:** A análise do ranking, baseada no número total de transações no período selecionado, **refuta** a hipótese de uma distribuição homogênea. O desempenho das agências varia significativamente, com o grupo das 3 melhores agências registrando um volume muito superior ao das 3 piores. Isso indica a necessidade de direcionar esforços para entender e melhorar a performance das agências com menor volume.
        """)
    with tab5:
         vw.criar_graficos_analises(df_final)
else:
    st.warning('Nenhum dado para exibir. Por favor, selecione uma agência.')
