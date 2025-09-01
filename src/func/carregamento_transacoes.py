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
        transacoes_df['data_transacao'] = pd.to_datetime(transacoes_df['data_transacao'], format='mixed', utc=True)
        transacoes_df['data_transacao'] = transacoes_df['data_transacao'].dt.tz_localize(None)
        capital_agencia_df = pd.merge( contas_df,transacoes_df, on='num_conta', how='left')
        capital_agencia_df = pd.merge( capital_agencia_df,agencias_df, on='cod_agencia', how='left')
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