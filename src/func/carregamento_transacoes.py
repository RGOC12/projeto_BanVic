import pandas as pd
import streamlit as st
import numpy as np
from pathlib import Path

pasta = Path("C:/Users/rgall/Documents/Projeto_BANVIC/src/data")

@st.cache_data
def dados_transacoes():
    agencias_df = pd.read_csv(pasta/'agencias.csv')
    transacoes_df = pd.read_csv(pasta/'transacoes.csv')
    contas_df = pd.read_csv(pasta/'contas.csv')
    transacoes_df['data_transacao'] = pd.to_datetime(
        transacoes_df['data_transacao'], format='mixed', utc=True
    )
    transacoes_df['data_transacao'] = transacoes_df['data_transacao'].dt.tz_localize(None)
    capital_agencia_df = pd.merge( contas_df,transacoes_df, on='num_conta', how='left')
    capital_agencia_df = pd.merge( capital_agencia_df,agencias_df, on='cod_agencia', how='left')
    capital_agencia_df.rename(columns={'data_abertura_y': 'data_abertura'}, inplace=True)
    return capital_agencia_df