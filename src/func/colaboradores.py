import streamlit as st

class desempenhoColab:
        def aprovacao_colab(df):
            df_final = df
            st.header("Análise de Desempenho de Funcionários e Agências")
            st.markdown("""
            Esta seção analisa o desempenho dos funcionários e agências com base no número de propostas de crédito aprovadas.
            É possível filtrar por agência para ver a performance individual dos colaboradores.
            """)

            # Filtrar apenas as propostas aprovadas
            propostas_aprovadas = df_final[df_final['status_proposta'] == 'Aprovada'].copy()

            # Agrupar por agência e colaborador para contar as propostas aprovadas
            # Renomeia as colunas para uma melhor visualização no gráfico
            ranking_por_agencia = propostas_aprovadas.groupby(['nome'])['cod_proposta'].count().reset_index()
            ranking_por_agencia = ranking_por_agencia.rename(columns={'nome': 'Agência', 'cod_proposta': 'Propostas Aprovadas'})
            return  ranking_por_agencia

        def get_propostas_aprovadas(df):
            propostas_aprovadas = df[df['status_proposta'] == 'Aprovada'].copy()
            return propostas_aprovadas