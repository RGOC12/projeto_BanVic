import streamlit as st
import plotly.express as px
from src.func import BalancoBanco as bb, Dados as dd


st.set_page_config(page_title="Banco VICTOR", layout="wide")
st.title("Análise de Dados - Banco VICTOR")

dados_carregado = dd.dados_transacoes()
dados_crescimento_df = bb.balanco_data(dados_carregado).reset_index()



fig = px.pie(dados_crescimento_df, names='nome', values='arrecadacao_total', title='Arrecadacao Total')
st.plotly_chart(fig)