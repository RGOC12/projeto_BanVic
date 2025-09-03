import pandas as pd
import streamlit as st

class contas_bancarias:
    def transacoes_contas(propostas_df, transacoes_df, contas_df, clientes_df):
        # Agrega dados de propostas por cliente
        propostas_por_cliente = propostas_df.groupby(['cod_cliente', 'status_proposta']).size().unstack(fill_value=0)
        propostas_por_cliente.columns.name = None
        propostas_por_cliente = propostas_por_cliente.reset_index()

        # Agrega dados de transações por cliente
        df_transacoes_contas = pd.merge(transacoes_df, contas_df[['num_conta', 'cod_cliente']], on='num_conta', how='left')
        df_transacoes_contas['Depósito'] = df_transacoes_contas['valor_transacao'].apply(lambda x: x if x > 0 else 0)
        df_transacoes_contas['Saque'] = df_transacoes_contas['valor_transacao'].apply(lambda x: -x if x < 0 else 0)
        
        saques_depositos_por_cliente = df_transacoes_contas.groupby('cod_cliente')[['Saque', 'Depósito']].sum().reset_index()
        
        # ⚠️ Alteração: Começa com a lista completa de clientes para evitar desaparecimentos
        # ⚠️ Alteração: Inclui o último nome para criar o nome completo
        df_analise = clientes_df[['cod_cliente', 'primeiro_nome', 'ultimo_nome']].copy()
        df_analise['nome_completo'] = df_analise['primeiro_nome'] + ' ' + df_analise['ultimo_nome']
        
        # ⚠️ Alteração: Faz um merge à esquerda para adicionar os dados de transação
        df_analise = pd.merge(df_analise, saques_depositos_por_cliente, on='cod_cliente', how='left')
        
        # ⚠️ Alteração: Faz outro merge à esquerda para adicionar os dados de propostas
        df_analise = pd.merge(df_analise, propostas_por_cliente, on='cod_cliente', how='left')
        
        # Preenche os valores que não foram encontrados com 0
        df_analise = df_analise.fillna(0)

        df_analise.drop(['cod_cliente', 'primeiro_nome', 'ultimo_nome'], axis=1, inplace=True)
        colunas_ordenadas = ['nome_completo'] + [col for col in df_analise.columns if col != 'nome_completo']
        df_analise = df_analise[colunas_ordenadas]

        total_clientes = clientes_df.shape[0]
        
        return {'df_analise': df_analise, 'total_clientes': total_clientes}
    
    def clientes_sem_proposta(propostas_filtradas, clientes_df, contas_df, agencias_df):
        clientes_com_propostas = propostas_filtradas['cod_cliente'].unique()
        
        df_sem_propostas = clientes_df[~clientes_df['cod_cliente'].isin(clientes_com_propostas)].copy()
        
        df_final = pd.merge(df_sem_propostas, contas_df[['cod_cliente', 'cod_agencia', 'data_abertura']], on='cod_cliente', how='left')
        df_final = pd.merge(df_final, agencias_df[['cod_agencia', 'nome']], on='cod_agencia', how='left')
        
        # ⚠️ Alteração: Inclui o último nome e cria a coluna 'nome_cliente' com o nome completo
        df_final['nome_cliente'] = df_final['primeiro_nome'] + ' ' + df_final['ultimo_nome']

        df_final = df_final[['nome', 'nome_cliente', 'data_abertura']]
        df_final.columns = ['nome_agencia', 'nome_cliente', 'data_abertura_conta']
        
        df_final['data_abertura_conta'] = pd.to_datetime(df_final['data_abertura_conta'], format='mixed', errors='coerce').dt.strftime('%d/%m/%Y')
        
        return df_final