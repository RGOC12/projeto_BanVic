import pandas as pd
import streamlit as st
from src.func import PropostaCredito as pc

class filtros:
    def filtrar_por_data(df, coluna_data="data_transacao"):
        df[coluna_data] = pd.to_datetime(df[coluna_data]).dt.tz_localize(None)

        min_data = df[coluna_data].min().date()
        max_data = df[coluna_data].max().date()

        st.sidebar.header("Filtros")
        data_inicio = st.sidebar.date_input("Data de Início", min_value=min_data, max_value=max_data, value=min_data)
        data_fim = st.sidebar.date_input("Data de Fim", min_value=min_data, max_value=max_data, value=max_data)

        if data_inicio > data_fim:
            st.warning("⚠️ A data inicial é maior que a final.")
            data_inicio, data_fim = data_fim, data_inicio
        df_filtrado = df[
            (df[coluna_data] >= pd.to_datetime(data_inicio)) &
            (df[coluna_data] <= pd.to_datetime(data_fim))
        ]
        return df_filtrado
    
    
    def filtrar_por_data_prop(df, coluna_data="data_entrada_proposta"):
        df[coluna_data] = pd.to_datetime(df[coluna_data]).dt.tz_localize(None)

        min_data = df[coluna_data].min().date()
        max_data = df[coluna_data].max().date()

        st.sidebar.header("Filtros")
        data_inicio = st.sidebar.date_input("Data de Início", min_value=min_data, max_value=max_data, value=min_data)
        data_fim = st.sidebar.date_input("Data de Fim", min_value=min_data, max_value=max_data, value=max_data)

        if data_inicio > data_fim:
            st.warning("⚠️ A data inicial é maior que a final.")
            data_inicio, data_fim = data_fim, data_inicio
        df_filtrado = df[
            (df[coluna_data] >= pd.to_datetime(data_inicio)) &
            (df[coluna_data] <= pd.to_datetime(data_fim))
        ]
        return df_filtrado
    
    
    def filtrar_df_por_agencia_e_data(df):
        data_porcentagens_df = df
        todas_agencias = data_porcentagens_df['nome'].unique()
        agencias_selecionadas = st.multiselect('Selecione as Agências:',options=todas_agencias,default=todas_agencias)
        df_filtrado_final = data_porcentagens_df[data_porcentagens_df['nome'].isin(agencias_selecionadas)]

        return df_filtrado_final
    
    def filtrar_por_data_cliente(df, data_inicio, data_fim, coluna_data="data_entrada_proposta"):
        df_filtrado = df[
            (df[coluna_data] >= pd.to_datetime(data_inicio)) &
            (df[coluna_data] <= pd.to_datetime(data_fim))
        ]
        return df_filtrado
    
    def filtrar_df_por_agencia(df, agencias_selecionadas):
       
        df_filtrado = df[df['nome'].isin(agencias_selecionadas)]
        return df_filtrado
    
    def filtrar_por_data_conclusao(df, data_inicio, data_fim, coluna_data="data_entrada_proposta"):
        df_filtrado = df[
                (df[coluna_data] >= pd.to_datetime(data_inicio)) &
                (df[coluna_data] <= pd.to_datetime(data_fim))
            ]
        return df_filtrado
    

    