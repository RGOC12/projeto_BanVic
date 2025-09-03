import pandas as pd
import streamlit as st
from pathlib import Path

pasta = Path("src/data")

class dados:
    
    @st.cache_data
    def dados_transacoes():
        agencias_df = pd.read_csv(pasta/'agencias.csv')
        transacoes_df = pd.read_csv(pasta/'transacoes.csv')
        contas_df = pd.read_csv(pasta/'contas.csv')
        
        # Carregar e tratar dados de desemprego
        desemprego_df = pd.read_csv(pasta/'desemprego.csv')
        desemprego_df.columns = desemprego_df.columns.str.strip()
        desemprego_df['data'] = pd.to_datetime(desemprego_df['data'])
        
        # Mesclar os DataFrames principais
        capital_agencia_df = pd.merge(contas_df, transacoes_df, on='num_conta', how='left')
        capital_agencia_df = pd.merge(capital_agencia_df, agencias_df, on='cod_agencia', how='left')
        
        # Converte a coluna de data para o formato correto
        capital_agencia_df['data_transacao'] = pd.to_datetime(capital_agencia_df['data_transacao'], format='mixed', utc=True)
        capital_agencia_df['data_transacao'] = capital_agencia_df['data_transacao'].dt.tz_localize(None)

        # Adicionar a taxa de desemprego à base de dados
        capital_agencia_df = pd.merge_asof(
            capital_agencia_df.sort_values('data_transacao'),
            desemprego_df.sort_values('data'),
            left_on='data_transacao',
            right_on='data',
            direction='nearest'
        )
        
        capital_agencia_df.rename(columns={'data_abertura_y': 'data_abertura'}, inplace=True)
        return capital_agencia_df
    
    @st.cache_data
    def dados_credito():
        propostas_df = pd.read_csv(pasta/'propostas_credito.csv')
        colaboradores_df = pd.read_csv(pasta/'colaboradores.csv')
        colaborador_agencia_df = pd.read_csv(pasta/'colaborador_agencia.csv')
        agencias_df = pd.read_csv(pasta/'agencias.csv')
        propostas_df['data_entrada_proposta'] = pd.to_datetime(propostas_df['data_entrada_proposta'], format='mixed', utc=True)
        propostas_df['data_entrada_proposta'] = propostas_df['data_entrada_proposta'].dt.tz_localize(None)
        propostas_df = pd.merge(propostas_df,colaboradores_df,on='cod_colaborador', how='left')
        propostas_df = pd.merge(propostas_df,colaborador_agencia_df,on='cod_colaborador', how='left')
        propostas_df = pd.merge(propostas_df,agencias_df,on='cod_agencia', how='left')
        return propostas_df
    
    @st.cache_data
    def cruzar_dados_com_desemprego():
        agencias_df = pd.read_csv(pasta / 'agencias.csv')
        transacoes_df = pd.read_csv(pasta / 'transacoes.csv')
        contas_df = pd.read_csv(pasta / 'contas.csv')
        desemprego_df = pd.read_csv(pasta / 'desemprego.csv')
        desemprego_df.columns = desemprego_df.columns.str.strip()
        desemprego_df['data'] = pd.to_datetime(desemprego_df['data'])
        capital_agencia_df = pd.merge(contas_df, transacoes_df, on='num_conta', how='left')
        capital_agencia_df = pd.merge(capital_agencia_df, agencias_df, on='cod_agencia', how='left')
        capital_agencia_df['data_transacao'] = pd.to_datetime(capital_agencia_df['data_transacao'], format='mixed', utc=True)
        capital_agencia_df['data_transacao'] = capital_agencia_df['data_transacao'].dt.tz_localize(None)
        capital_agencia_df = capital_agencia_df.sort_values('data_transacao')
        desemprego_df = desemprego_df.sort_values('data')
        capital_agencia_df = pd.merge_asof(
            capital_agencia_df,
            desemprego_df,
            left_on='data_transacao',
            right_on='data',
            direction='nearest'
        )
        capital_agencia_df.rename(columns={'data_abertura_y': 'data_abertura'}, inplace=True)
        return capital_agencia_df
    
    @st.cache_data
    def dados_colaboradores():
        df_agencias = pd.read_csv(pasta / "agencias.csv")
        df_colaboradores = pd.read_csv(pasta / "colaboradores.csv")
        df_colaborador_agencia = pd.read_csv(pasta / "colaborador_agencia.csv")
        df_propostas = pd.read_csv(pasta / "propostas_credito.csv")
        df_completo = pd.merge(df_propostas, df_colaboradores, on='cod_colaborador', how='left')
        df_completo = pd.merge(df_completo, df_colaborador_agencia, on='cod_colaborador', how='left')
        df_final = pd.merge(df_completo, df_agencias, on='cod_agencia', how='left')
        return df_final
    
    @st.cache_data
    def dados_para_analise():
        """
        Carrega, converte e retorna todos os DataFrames de dados.
        """
        propostas_df = pd.read_csv(pasta / 'propostas_credito.csv')
        contas_df = pd.read_csv(pasta / 'contas.csv')
        transacoes_df = pd.read_csv(pasta / 'transacoes.csv')
        clientes_df = pd.read_csv(pasta / 'clientes.csv')
        
        propostas_df['cod_cliente'] = propostas_df['cod_cliente'].astype(str)
        contas_df['cod_cliente'] = contas_df['cod_cliente'].astype(str)
        clientes_df['cod_cliente'] = clientes_df['cod_cliente'].astype(str)
        transacoes_df['num_conta'] = transacoes_df['num_conta'].astype(str)
        contas_df['num_conta'] = contas_df['num_conta'].astype(str)

        return propostas_df, contas_df, transacoes_df, clientes_df