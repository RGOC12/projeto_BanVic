import pandas as pd
import streamlit as st
from pathlib import Path

pasta = Path("src/data")

class Dados:
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
    
    def cruzar_dados_com_desemprego():
        try:
            agencias_df = pd.read_csv(pasta / 'agencias.csv')
            transacoes_df = pd.read_csv(pasta / 'transacoes.csv')
            contas_df = pd.read_csv(pasta / 'contas.csv')
            desemprego_df = pd.read_csv(pasta / 'desemprego.csv')
        except FileNotFoundError as e:
            print(f"Erro: Arquivo não encontrado. Verifique se os arquivos CSV estão na pasta 'src/data'. Erro: {e}")
            return None

        # Tratar a coluna de data do DataFrame de desemprego
        desemprego_df.columns = desemprego_df.columns.str.strip()
        desemprego_df['data'] = pd.to_datetime(desemprego_df['data'])
        # if 'Date' in desemprego_df.columns:
        #     desemprego_df['data'] = pd.to_datetime(desemprego_df['Date'])
        # elif 'Data' in desemprego_df.columns:
        #     desemprego_df['data'] = pd.to_datetime(desemprego_df['Data'])
        # else:
        # # If the column name is unknown, you could print the available columns for debugging
        #     print("Columns in desemprego_df:", desemprego_df.columns)
        # # Or raise a custom error
        #     raise KeyError("Could not find a 'data' or 'Date' column in desemprego.csv")
        # # Mesclar os DataFrames principais (contas, transacoes e agencias)
        capital_agencia_df = pd.merge(contas_df, transacoes_df, on='num_conta', how='left')
        capital_agencia_df = pd.merge(capital_agencia_df, agencias_df, on='cod_agencia', how='left')
        
        # Converte a coluna de data de transação para o formato correto
        capital_agencia_df['data_transacao'] = pd.to_datetime(capital_agencia_df['data_transacao'], format='mixed', utc=True)
        capital_agencia_df['data_transacao'] = capital_agencia_df['data_transacao'].dt.tz_localize(None)

        # Ordena os DataFrames para a junção 'merge_asof'
        capital_agencia_df = capital_agencia_df.sort_values('data_transacao')
        desemprego_df = desemprego_df.sort_values('data')
        
        # Adicionar a taxa de desemprego à base de dados
        # O 'merge_asof' associa a transação à taxa de desemprego mais próxima
        capital_agencia_df = pd.merge_asof(
            capital_agencia_df,
            desemprego_df,
            left_on='data_transacao',
            right_on='data',
            direction='nearest'
        )
        
        # Renomear colunas para evitar conflitos
        capital_agencia_df.rename(columns={'data_abertura_y': 'data_abertura'}, inplace=True)
        
        return capital_agencia_df