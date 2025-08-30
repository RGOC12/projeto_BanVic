import numpy as np
import pandas as pd


class AnaliseBanco:
    
    def balanco_data(balanco):
        balanco_df = balanco.copy()
        balanco_df['depositos'] = np.where(balanco_df['valor_transacao'] > 0, balanco_df['valor_transacao'], 0)
        balanco_df['saques'] = np.where(balanco_df['valor_transacao'] < 0, balanco_df['valor_transacao'], 0)
        balanco_df['arrecadacao_total'] = balanco_df['depositos'] + balanco_df['saques']
        balanco_df = balanco_df.groupby(['data_abertura','nome', 'uf','tipo_agencia']).agg(num_transacoes=('num_conta', 'count'),total_saques=('saques','sum'),total_depositos=('depositos','sum'), arrecadacao_total = ('arrecadacao_total','sum'))
        return balanco_df

    def estatistica_data(balanco):
        balanco_df = balanco.copy()
        balanco_df['depositos'] = np.where(balanco_df['valor_transacao'] > 0, balanco_df['valor_transacao'], 0)
        balanco_df['saques'] = np.where(balanco_df['valor_transacao'] < 0, balanco_df['valor_transacao'], 0)
        balanco_df['arrecadacao_total'] = balanco_df['depositos'] + balanco_df['saques']
        balanco_df['data_transacao'] = pd.to_datetime(balanco_df['data_transacao']).dt.year
        balanco_df = balanco_df.groupby(['nome','data_transacao',]).agg(arrecadacao_total = ('arrecadacao_total','sum'))
        return balanco_df

    def transacoes_data(balanco):
        balanco_df = balanco.copy()
        balanco_df['data_transacao'] = pd.to_datetime(balanco_df['data_transacao']).dt.strftime('%Y-%m')
        balanco_df = balanco_df.groupby(['nome','data_transacao',]).agg(num_transacoes=('num_conta', 'count'))
        return balanco_df