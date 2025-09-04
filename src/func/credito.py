import numpy as np 
import pandas as pd
class PropostaCredito:
    
    def propostas_status(propostas): 
        propostas_df = propostas.copy()

        # Se o DataFrame estiver vazio, retorna ele mesmo sem erro
        if propostas_df.empty:
            return propostas_df

        # Marca status em colunas auxiliares
        propostas_df['enviadas'] = propostas_df['status_proposta'].where(propostas_df['status_proposta'] == 'Enviada') 
        propostas_df['aprovada'] = propostas_df['status_proposta'].where(propostas_df['status_proposta'] == 'Aprovada') 
        propostas_df['em_analise'] = propostas_df['status_proposta'].where(propostas_df['status_proposta'] == 'Em análise') 
        propostas_df['validacao_documentos'] = propostas_df['status_proposta'].where(propostas_df['status_proposta'] == 'Validação documentos') 

        # Faz o agrupamento por nome e data
        propostas_df = propostas_df.groupby(['nome','data_abertura']).agg(
            enviadas=('enviadas','count'),
            aprovadas=('aprovada','count'),
            em_analise=('em_analise','count'),
            validacao_documentos=('validacao_documentos','count')
        )

        # Calcula totais e taxa de aprovação
        propostas_df['total_propostas'] = (
            propostas_df['enviadas'] +
            propostas_df['aprovadas'] +
            propostas_df['em_analise'] +
            propostas_df['validacao_documentos']
        )

        # Evita divisão por zero
        propostas_df['taxa_aprovacao'] = 0
        mask = propostas_df['total_propostas'] > 0
        propostas_df.loc[mask, 'taxa_aprovacao'] = (
            (propostas_df.loc[mask, 'aprovadas'] / propostas_df.loc[mask, 'total_propostas']) * 100
        ).round(2).astype(str) + '%'

        return propostas_df

    
    def propostas_media(propostas):
        propostas_df = propostas.copy()
        aprovacao_df = PropostaCredito.propostas_status(propostas).reset_index()
        propostas_df = propostas_df.groupby(['nome']).agg(carencia_media=('carencia','mean'),taxa_juros_mensal=('taxa_juros_mensal','mean'),quantidade_parcelas=('quantidade_parcelas','max')).reset_index()
        propostas_df = propostas_df.merge(aprovacao_df[['nome','taxa_aprovacao','total_propostas']], on='nome', how='left')
        propostas_df['carencia_media'] = (propostas_df['carencia_media']).round(0)
        return propostas_df
    
    def data_porcentagens(propostas):
        propostas_df = propostas.copy()
        propostas_df['data_entrada_proposta'] = pd.to_datetime(propostas_df['data_entrada_proposta']).dt.strftime('%Y')
        # Mapeia os status para valores numéricos.
        propostas_df['enviadas'] = propostas_df['status_proposta'].apply(lambda x: 1 if x == 'Enviada' else 0)
        propostas_df['aprovadas'] = propostas_df['status_proposta'].apply(lambda x: 1 if x == 'Aprovada' else 0)
        propostas_df['em_analise'] = propostas_df['status_proposta'].apply(lambda x: 1 if x == 'Em análise' else 0)
        propostas_df['validacao_documentos'] = propostas_df['status_proposta'].apply(lambda x: 1 if x == 'Validação documentos' else 0)
        df_agrupado = propostas_df.groupby(['nome', 'data_entrada_proposta']).agg(
            enviadas=('enviadas', 'sum'),
            aprovadas=('aprovadas', 'sum'),
            em_analise=('em_analise', 'sum'),
            validacao_documentos=('validacao_documentos', 'sum')
        ).reset_index()

        
        df_agrupado['taxa_aprovacao'] = ((df_agrupado['aprovadas'] / (
            df_agrupado['enviadas'] +
            df_agrupado['aprovadas'] +
            df_agrupado['em_analise'] +
            df_agrupado['validacao_documentos']
        )) * 100).round(2)

        # Retorna o DataFrame com as colunas finais
        return df_agrupado[['nome', 'data_entrada_proposta', 'taxa_aprovacao']]