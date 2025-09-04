import streamlit as st
import pandas as pd
import plotly.express as px
from src.func import filtros as ft, dados as dd, desempenhoColab as dc

# 1. Carregar e filtrar os dados com as suas funções
st.title("Análise de Desempenho de Funcionários e Agências")
dados = dd.dados_colaboradores()
filtro_data = ft.filtrar_por_data_prop(dados)
propostas_aprovadas = dc.get_propostas_aprovadas(filtro_data)

# 2. Criar o filtro de agência
todas_agencias = propostas_aprovadas['nome'].unique()
agencias = ['Todas'] + sorted(todas_agencias.tolist())
agencia_selecionada = st.selectbox('Selecione uma Agência:', agencias)

if agencia_selecionada == 'Todas':
    # Agrupar por agência para o ranking geral
    st.subheader('Ranking de Desempenho por Agência')
    ranking_por_agencia = propostas_aprovadas.groupby(['nome'])['cod_proposta'].count().reset_index()
    ranking_por_agencia = ranking_por_agencia.rename(columns={'nome': 'Agência', 'cod_proposta': 'Propostas Aprovadas'})
    
    # Criar abas para a visualização
    tabela_tab, grafico_tab = st.tabs(["Tabela", "Gráfico"])
    
    with tabela_tab:
        st.dataframe(ranking_por_agencia.sort_values(by='Propostas Aprovadas', ascending=False).reset_index(drop=True))
        
    with grafico_tab:
        st.bar_chart(ranking_por_agencia.set_index('Agência'))
        

else:
    # --- Lógica para incluir funcionários com 0 aprovações ---
    st.subheader(f'Desempenho dos Funcionários da {agencia_selecionada}')
    
    # 1. Obter a lista completa de funcionários da agência
    todos_funcionarios_agencia = filtro_data[filtro_data['nome'] == agencia_selecionada].drop_duplicates(subset=['cod_colaborador'])
    
    # 2. Contar as propostas aprovadas apenas para essa agência
    propostas_aprovadas_agencia = propostas_aprovadas[propostas_aprovadas['nome'] == agencia_selecionada].copy()
    aprovacoes_por_colab = propostas_aprovadas_agencia.groupby('cod_colaborador')['cod_proposta'].count().reset_index()
    aprovacoes_por_colab.rename(columns={'cod_proposta': 'Propostas Aprovadas'}, inplace=True)
    
    # 3. Mesclar as duas listas para incluir os zeros
    ranking_funcionarios = pd.merge(
        todos_funcionarios_agencia[['cod_colaborador', 'primeiro_nome', 'ultimo_nome', 'nome']],
        aprovacoes_por_colab,
        on='cod_colaborador',
        how='left'
    )
    
    # 4. Preencher os valores nulos com 0 e converter para inteiro
    ranking_funcionarios['Propostas Aprovadas'] = ranking_funcionarios['Propostas Aprovadas'].fillna(0).astype(int)
    
    # 5. Criar o nome completo e renomear colunas
    ranking_funcionarios['nome_completo'] = ranking_funcionarios['primeiro_nome'] + ' ' + ranking_funcionarios['ultimo_nome']
    ranking_funcionarios = ranking_funcionarios.rename(columns={'nome': 'Agência'})
    
    # Ordenar os dados para exibição
    ranking_funcionarios = ranking_funcionarios.sort_values(by='Propostas Aprovadas', ascending=False).reset_index(drop=True)

    # Criar abas para a visualização
    tabela_tab, grafico_tab = st.tabs(["Tabela de Desempenho", "Gráfico de Desempenho"])
    
    with tabela_tab:
        st.dataframe(ranking_funcionarios[['nome_completo', 'Propostas Aprovadas', 'Agência']])
    
    with grafico_tab:
        fig = px.bar(
            ranking_funcionarios,
            x='nome_completo',
            y='Propostas Aprovadas',
            color='Agência',
            title=f'Ranking de Propostas Aprovadas - Agência {agencia_selecionada}'
        )
        fig.update_layout(xaxis_title="Funcionário", yaxis_title="Nº de Propostas Aprovadas")
        st.plotly_chart(fig, use_container_width=True)


        