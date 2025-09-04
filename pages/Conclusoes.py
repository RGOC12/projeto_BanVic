import pandas as pd
import streamlit as st
from src.func import BalancoBanco as bb, dados as dd, filtros as ft, view as vw
import numpy as np
import plotly.graph_objects as go

df_original = dd.dados_transacoes()
df_analise = dd.cruzar_dados_com_desemprego()

# --- Centralize os filtros na barra lateral e use st.session_state ---

st.sidebar.header("Filtros para Análise")

# Aplica o filtro de data (usando a sua função)
df_filtrado_por_data = ft.filtrar_por_data(df_analise)

# Aplica o filtro de agência
agencias = ['Todas'] + sorted(df_filtrado_por_data['nome'].unique().tolist())
agencia_selecionada = st.sidebar.selectbox("Filtrar por Agência:", agencias)

df_final = df_filtrado_por_data
if agencia_selecionada != 'Todas':
    df_final = df_filtrado_por_data[df_filtrado_por_data['nome'] == agencia_selecionada]

# Armazena o DataFrame filtrado no estado da sessão para uso em todas as guias
st.session_state.df_final = df_final

# --- Fim da seção de filtros centralizados ---

tab1, tab2, tab3= st.tabs(["Análise Taxa de Desemprego vs Transações Bancárias", "Análise de Transações", "Ranking de Agências"])

with tab1:
    if st.session_state.df_final is None or st.session_state.df_final.empty:
        st.warning("Nenhum dado para exibir com os filtros selecionados.")
    else:
        df_agrupado = st.session_state.df_final.groupby(st.session_state.df_final['data_transacao'].dt.to_period('M')).agg(
            total_transacoes=('valor_transacao', 'sum'),
            media_desemprego=('taxa_desemprego', 'mean')
        ).reset_index()
        df_agrupado['data_transacao'] = df_agrupado['data_transacao'].dt.to_timestamp()
        
        st.header("1. Análise da Relação entre Taxa de Desemprego e Transações Bancárias")
        st.markdown("""
        Esta seção compara o volume total de transações bancárias com a taxa de desemprego ao longo do tempo.
        O objetivo é identificar possíveis correlações entre a saúde econômica geral (indicada pelo desemprego)
        e o comportamento financeiro dos clientes do BanVic.
        """)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_agrupado['data_transacao'], y=df_agrupado['media_desemprego'],
                                 mode='lines+markers',
                                 name='Taxa de Desemprego (%)',
                                 yaxis='y1',
                                 line=dict(color='red')))
        fig.add_trace(go.Scatter(x=df_agrupado['data_transacao'], y=df_agrupado['total_transacoes'],
                                 mode='lines+markers',
                                 name='Valor Total Transações (R$)',
                                 yaxis='y2',
                                 line=dict(color='blue')))
        fig.update_layout(
            title='Taxa de Desemprego vs. Valor Total de Transações ao Longo do Tempo',
            xaxis_title='Data',
            yaxis=dict(
                title=dict(
                    text='Taxa de Desemprego (%)', 
                    font=dict(color='red')
                ),
                tickfont=dict(color='red')
            ),
            yaxis2=dict(
                title=dict(
                    text='Valor Total Transações (R$)',
                    font=dict(color='blue')
                ),
                tickfont=dict(color='blue'),
                overlaying='y',
                side='right'
            ),
            legend=dict(x=0.01, y=0.99),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Observações e Justificativa")
        st.write(f"""
        O gráfico acima apresenta a evolução da taxa de desemprego e o valor total das transações realizadas pelas agências do BanVic (para a agência '{agencia_selecionada}' se selecionada).
        
        É possível observar se existe alguma **correlação visual** entre os movimentos da taxa de desemprego e o volume/valor das transações.
        * **Exemplo de Correlação Negativa (hipotético):** Se a linha vermelha (desemprego) sobe e a linha azul (transações) desce, pode indicar que períodos de maior desemprego estão associados a uma menor movimentação financeira.
        * **Exemplo de Ausência de Correlação:** Se as linhas se movem de forma independente, pode sugerir que, no período analisado, a taxa de desemprego não é o fator principal que impulsiona o volume de transações bancárias para esta base de dados específica.

        Para uma análise mais robusta, seria necessário aplicar métodos estatísticos (como correlação de Pearson) e considerar um período de tempo mais extenso, além de outros fatores macroeconômicos.
        """)
        
        st.subheader("Tabela de Dados Agrupados")
        st.dataframe(df_agrupado.rename(columns={
            'data_transacao': 'Data (Mês)', 
            'total_transacoes': 'Valor Total Transações', 
            'media_desemprego': 'Média Taxa Desemprego'
        }))
        
        st.header("2. Proposta de Dados Públicos e Valor para o BanVic")
        st.markdown("""
        Para enriquecer ainda mais a base de dados do BanVic e ampliar as análises, sugerimos a incorporação das seguintes fontes de dados públicas:
        """)
        st.markdown("""
        ---
        **Outras fontes potenciais:**
        * **Dados Demográficos e Renda per Capita por Município (IBGE):** Para segmentar clientes e otimizar campanhas de marketing por região.
        * **Taxa Selic (Banco Central do Brasil):** Impacta diretamente o custo do crédito e o rendimento de investimentos, sendo crucial para a precificação de produtos.
        """)

        st.header("3. Decisões Facilitadas com o Uso de Novos Dados")
        st.markdown("""
        A integração desses dados externos no Data Warehouse do BanVic facilitaria uma série de decisões estratégicas e operacionais:
        """)
        st.subheader("a) Gestão Proativa de Risco de Crédito")
        st.write("""
        * Monitorar agências em regiões com aumento da taxa de desemprego e/ou inflação.
        * Antecipar um possível aumento da inadimplência e oferecer, proativamente, programas de renegociação de dívidas ou suporte financeiro antes que os problemas se agravem.
        * Ajustar os modelos de score de crédito para incorporar variáveis macroeconômicas.
        """)
        st.subheader("b) Otimização do Desenvolvimento e Oferta de Produtos")
        st.write("""
        * Desenvolver produtos financeiros adaptados a cenários econômicos específicos (ex: microcrédito em regiões de alto desemprego, ou produtos de investimento com maior rentabilidade real em períodos de alta inflação).
        * Personalizar campanhas de marketing e ofertas de produtos para clientes em diferentes contextos socioeconômicos.
        """)
        st.subheader("c) Planejamento Estratégico e de Expansão")
        st.write("""
        * Tomar decisões mais informadas sobre a abertura de novas agências ou o fechamento/reestruturação de unidades existentes, considerando o potencial econômico e demográfico de cada região.
        * Alocar recursos de forma mais eficiente, direcionando investimentos para áreas com maior potencial de crescimento.
        """)
        st.subheader("d) Análise de Sensibilidade e Cenários")
        st.write("""
        * Realizar simulações de cenários econômicos (otimista, realista, pessimista) e prever o impacto nas receitas, despesas e na base de clientes do banco.
        * Avaliar a resiliência do portfólio de crédito do banco a choques econômicos.
        """)


with tab2:
    if 'df_final' in st.session_state and not st.session_state.df_final.empty:
        vw.criar_graficos_analises(st.session_state.df_final)
    else:
        st.warning("Nenhum dado para exibir. Por favor, ajuste os filtros na guia 'Tabela de Dados'.")

with tab3:
    if 'df_final' in st.session_state and not st.session_state.df_final.empty:
        st.header('Ranking de Agências por Número de Transações')
        ranking_df = bb.ranking_transacoes(st.session_state.df_final)
        st.subheader('Ranking Completo')
        st.dataframe(ranking_df)
        st.bar_chart(ranking_df.set_index('nome'))
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
    else:
        st.warning("Nenhum dado para exibir. Por favor, ajuste os filtros na guia 'Tabela de Dados'.")