import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from src.func import BalancoBanco as bb # Importa a classe com as novas funções

class view:
    def criar_graficos_analises(df_final):
        # Análise por Dia da Semana
        st.header('Análise de Transações por Dia da Semana')
        
        # Executa a função de análise
        analise_dia_semana_df = bb.analise_por_dia_semana(df_final)
        
        # Exibe o gráfico de barras
        st.bar_chart(
            analise_dia_semana_df.set_index('dia_semana')[['media_transacoes', 'volume_medio_movimentado']]
        )
        
        # Exibe a tabela com os dados brutos
        st.subheader('Dados Detalhados por Dia da Semana')
        st.dataframe(analise_dia_semana_df)
        
        # Conclusão da análise
        dia_maior_media = analise_dia_semana_df.loc[analise_dia_semana_df['media_transacoes'].idxmax()]['dia_semana']
        dia_maior_volume = analise_dia_semana_df.loc[analise_dia_semana_df['volume_medio_movimentado'].idxmax()]['dia_semana']
        
        st.markdown(f"""
        **Conclusão:**
        * O dia da semana com a maior média de transações aprovadas é a **{dia_maior_media}**.
        * O dia com o maior volume médio movimentado é a **{dia_maior_volume}**.
        """)

        # ---
        
        # Análise de Meses Pares e Ímpares
        st.header('Volume Médio de Transações: Meses Pares vs. Ímpares')

        # Executa a função de análise e o teste estatístico
        volume_meses, t_stat, p_valor = bb.analise_meses_par_impar(df_final)

        # Exibe o gráfico de barras para a comparação
        st.bar_chart(
            volume_meses.set_index('mes_tipo')
        )
        
        # Exibe a tabela com os dados brutos
        st.subheader('Volume Médio por Tipo de Mês')
        st.dataframe(volume_meses.set_index('mes_tipo'))

        # Conclusão da análise com o resultado do teste estatístico
        if p_valor < 0.05:
            conclusao_estatistica = "A análise **VALIDA** a afirmação. A diferença entre o volume médio de transações nos meses pares e ímpares é estatisticamente significativa."
        else:
            conclusao_estatistica = "A análise **REFUTA** a afirmação. A diferença observada no volume médio de transações entre os meses pares e ímpares **NÃO É** estatisticamente significativa."

        st.markdown(f"""Conclusão: {conclusao_estatistica}""")