import pandas as pd
import streamlit as st
from src.func import BalancoBanco as bb, dados as dd, filtros as ft, view as vw
import numpy as np
import plotly.graph_objects as go


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
    df_analise = dd.cruzar_dados_com_desemprego()

    if df_analise is None:
        st.warning("Não foi possível carregar os dados para análise de desemprego.")
    else:
        # --- Filtros (opcional, mas recomendado para granularidade) ---
        st.sidebar.header("Filtros para Análise")
        
        # Exemplo de filtro de data
        min_date = df_analise['data_transacao'].min().to_pydatetime().date()
        max_date = df_analise['data_transacao'].max().to_pydatetime().date()

        date_range = st.sidebar.date_input(
            "Selecione o período:",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )

        if len(date_range) == 2:
            start_date, end_date = date_range
            df_filtrado = df_analise[
                (df_analise['data_transacao'].dt.date >= start_date) &
                (df_analise['data_transacao'].dt.date <= end_date)
            ]
        else:
            df_filtrado = df_analise
        
        # Filtro de agência (se aplicável e você tiver a função em filtros.py)
        agencias = ['Todas'] + sorted(df_filtrado['nome'].unique().tolist())
        agencia_selecionada = st.sidebar.selectbox("Filtrar por Agência:", agencias)

        if agencia_selecionada != 'Todas':
            df_filtrado = df_filtrado[df_filtrado['nome'] == agencia_selecionada]

        if df_filtrado.empty:
            st.warning("Nenhum dado para exibir com os filtros selecionados.")
        else:
            # --- Agrupar dados para o gráfico ---
            # Agrupar por data (para simplificar a visualização do gráfico)
            df_agrupado = df_filtrado.groupby(df_filtrado['data_transacao'].dt.to_period('M')).agg(
                total_transacoes=('valor_transacao', 'sum'),
                media_desemprego=('taxa_desemprego', 'mean')
            ).reset_index()
            df_agrupado['data_transacao'] = df_agrupado['data_transacao'].dt.to_timestamp()


            # --- Seção: Análise da Relação com a Taxa de Desemprego ---
            st.header("1. Análise da Relação entre Taxa de Desemprego e Transações Bancárias")
            st.markdown("""
            Esta seção compara o volume total de transações bancárias com a taxa de desemprego ao longo do tempo.
            O objetivo é identificar possíveis correlações entre a saúde econômica geral (indicada pelo desemprego)
            e o comportamento financeiro dos clientes do BanVic.
            """)

            # Gráfico Combinado
            fig = go.Figure()

            # Adicionar linha para Taxa de Desemprego
            fig.add_trace(go.Scatter(x=df_agrupado['data_transacao'], y=df_agrupado['media_desemprego'],
                                    mode='lines+markers',
                                    name='Taxa de Desemprego (%)',
                                    yaxis='y1',
                                    line=dict(color='red')))

            # Adicionar linha para Valor Total das Transações
            fig.add_trace(go.Scatter(x=df_agrupado['data_transacao'], y=df_agrupado['total_transacoes'],
                                    mode='lines+markers',
                                    name='Valor Total Transações (R$)',
                                    yaxis='y2',
                                    line=dict(color='blue')))

            # Configurar layout do gráfico
            fig.update_layout(

                title='Taxa de Desemprego vs. Valor Total de Transações ao Longo do Tempo',
                xaxis_title='Data',
                yaxis=dict(
                    title=dict(
                        text='Taxa de Desemprego (%)', # O texto do título vai aqui
                        font=dict(color='red')        # A fonte do título vai aqui dentro
                    ),
                    tickfont=dict(color='red')        # A fonte dos rótulos (ticks) vai aqui
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
            O gráfico acima apresenta a evolução da taxa de desemprego e o valor total das transações realizadas pelas agências do BanVic (filtrado até {end_date.strftime('%d/%m/%Y')} e para a agência '{agencia_selecionada}' se selecionada).
            
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

            # --- Seção: Proposta de Dados Públicos e Valor ---
            st.header("2. Proposta de Dados Públicos e Valor para o BanVic")
            st.markdown("""
            Para enriquecer ainda mais a base de dados do BanVic e ampliar as análises, sugerimos a incorporação das seguintes fontes de dados públicas:
            """)
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("a) Taxa de Desemprego (IBGE)")
                st.write("""
                * **Fonte:** Instituto Brasileiro de Geografia e Estatística (IBGE), através de pesquisas como a PNAD Contínua.
                * **Valor:** Permite ao BanVic correlacionar a saúde financeira de seus clientes com a situação econômica do mercado de trabalho. Ajuda a entender se aumentos ou quedas no desemprego em uma região afetam o volume de depósitos, saques, ou a procura por crédito.
                """)
            with col2:
                st.subheader("b) Índice Nacional de Preços ao Consumidor Amplo (IPCA - IBGE)")
                st.write("""
                * **Fonte:** Instituto Brasileiro de Geografia e Estatística (IBGE).
                * **Valor:** Fornece o indicador oficial de inflação no Brasil. Ao entender a evolução do poder de compra, o banco pode ajustar ofertas de produtos (ex: investimentos indexados à inflação, linhas de crédito com juros mais competitivos) e prever a demanda por serviços em um cenário de custos crescentes.
                """)
            
            st.markdown("""
            ---
            **Outras fontes potenciais:**
            * **Dados Demográficos e Renda per Capita por Município (IBGE):** Para segmentar clientes e otimizar campanhas de marketing por região.
            * **Taxa Selic (Banco Central do Brasil):** Impacta diretamente o custo do crédito e o rendimento de investimentos, sendo crucial para a precificação de produtos.
            """)

            # --- Seção: Decisões Facilitadas com o Uso desses Novos Dados ---
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
