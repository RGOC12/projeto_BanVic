import streamlit as st
import plotly.express as px
from src.func import PropostaCredito as pc, dados as dd,filtros as ft

dados_df = dd.dados_credito()
df_filtrado_por_data = ft.filtrar_por_data_prop(dados_df)

tab1, tab2, tab3, tab4 = st.tabs(["Propostas por periodo", "Proprotas aprovadas", "media aprovação", "Grafico de taxa de aprovação"])

with tab1:
    status_credito = pc.propostas_status(df_filtrado_por_data).reset_index()
    data_dados_df = status_credito[['data_abertura','nome','enviadas','aprovadas','em_analise','validacao_documentos','total_propostas','taxa_aprovacao']]
    st.dataframe(data_dados_df, hide_index=True)
    

with tab2:
    status_credito = pc.propostas_status(df_filtrado_por_data).reset_index()
    fig = px.pie(status_credito, names='nome', values='total_propostas', title='proprotas aprovadas')
    st.plotly_chart(fig)

with tab3:
    propostas_media_df = pc.propostas_media(df_filtrado_por_data)
    st.dataframe(propostas_media_df, hide_index=True)

with tab4:
    df_filtro = ft.filtrar_df_por_agencia_e_data(df_filtrado_por_data)
    data_porcentagens_df = pc.data_porcentagens(df_filtro)

    if not data_porcentagens_df.empty:
        balanco_crescimento_df = data_porcentagens_df.pivot(
            index='data_entrada_proposta', 
            columns='nome', 
            values='taxa_aprovacao'
        )
        st.line_chart(balanco_crescimento_df)
    else:
        st.warning('Nenhum dado para exibir. Selecione uma agência.')