import numpy as np
import pandas as pd
from scipy import stats

class BalancoBanco:
    
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
        balanco_df['data_transacao'] = pd.to_datetime(balanco_df['data_transacao']).dt.strftime('%Y-%m')
        balanco_df = balanco_df.groupby(['nome','data_transacao',]).agg(arrecadacao_total = ('arrecadacao_total','sum'))
        return balanco_df

    def transacoes_data(balanco):
        balanco_df = balanco.copy()
        balanco_df['data_transacao'] = pd.to_datetime(balanco_df['data_transacao']).dt.strftime('%Y-%m')
        balanco_df = balanco_df.groupby(['nome','data_transacao',]).agg(num_transacoes=('num_conta', 'count'))
        return balanco_df
    
    def analise_por_dia_semana(balanco):
        balanco_df = balanco.copy()
        
        # Converte a coluna para o formato de data
        balanco_df['data_transacao'] = pd.to_datetime(balanco_df['data_transacao'])
        
        # Cria uma coluna com o nome do dia da semana em português
        dias_semana_map = {0: 'segunda-feira', 1: 'terça-feira', 2: 'quarta-feira',
                           3: 'quinta-feira', 4: 'sexta-feira', 5: 'sábado', 6: 'domingo'}
        balanco_df['dia_semana'] = balanco_df['data_transacao'].dt.dayofweek.map(dias_semana_map)
        
        # Filtra por transações aprovadas (assumindo que há uma coluna 'status')
        # balanco_aprovadas = balanco_df[balanco_df['status'] == 'Aprovada']
        
        # Agrupa por dia da semana e calcula as médias
        analise_dia_semana = balanco_df.groupby('dia_semana').agg(
            media_transacoes=('num_conta', 'count'), # Usa 'num_conta' como proxy para contagem
            volume_medio_movimentado=('valor_transacao', 'mean')
        ).reset_index()
        
        # Ordena para melhor visualização
        analise_dia_semana['dia_semana'] = pd.Categorical(analise_dia_semana['dia_semana'],
                                                          categories=dias_semana_map.values(),
                                                          ordered=True)
        analise_dia_semana = analise_dia_semana.sort_values('dia_semana')
        
        return analise_dia_semana
    
    def analise_meses_par_impar(balanco):
        balanco_df = balanco.copy()
        
        # Converte a coluna para o formato de data
        balanco_df['data_transacao'] = pd.to_datetime(balanco_df['data_transacao'])
        
        # Cria uma coluna para identificar se o mês é par ou ímpar
        balanco_df['mes_tipo'] = balanco_df['data_transacao'].dt.month.apply(
            lambda x: 'par' if x % 2 == 0 else 'ímpar'
        )
        
        # Calcula o volume médio por tipo de mês
        volume_meses = balanco_df.groupby('mes_tipo')['valor_transacao'].mean().reset_index()
        
        # Realiza o teste estatístico (Teste t de Student)
        volume_par = balanco_df[balanco_df['mes_tipo'] == 'par']['valor_transacao']
        volume_impar = balanco_df[balanco_df['mes_tipo'] == 'ímpar']['valor_transacao']
        
        # stats.ttest_ind compara as médias de duas amostras independentes
        t_stat, p_valor = stats.ttest_ind(volume_par, volume_impar, equal_var=False, nan_policy='omit')
        
        return volume_meses, t_stat, p_valor
    
    def ranking_transacoes(balanco):
        balanco_df = balanco.copy()
        
        # Agrupa por nome da agência e conta o número de transações
        ranking_df = balanco_df.groupby('nome').agg(
            total_transacoes=('num_conta', 'count')
        ).reset_index()
        
        # Ordena o DataFrame pelo total de transações em ordem decrescente
        ranking_df = ranking_df.sort_values(by='total_transacoes', ascending=False)
        
        return ranking_df
    
    def analise_selic(balanco):
        # Transforma a data para o formato YYYY-MM para agrupar
        balanco_df = balanco.copy()
        balanco_df['data_mes'] = balanco_df['data_transacao'].dt.to_period('M').astype(str)
        # Agrupa os dados para obter o volume de transações e a Selic média do mês
        analise_df = balanco_df.groupby('data_mes').agg(
            volume_total=('valor_transacao', 'sum'),
            selic_media=('selic', 'mean')
        ).reset_index()

        df_para_correlacao = analise_df.dropna()

    # Verifica se há dados suficientes para o cálculo
        if len(df_para_correlacao) < 2 or df_para_correlacao['selic_media'].std() == 0 or df_para_correlacao['volume_total'].std() == 0:
            correlacao = 'Dados insuficientes ou constantes.'
        else:
        # Calcula a correlação
            correlacao = np.corrcoef(df_para_correlacao['volume_total'], df_para_correlacao['selic_media'])[0, 1]


        print(correlacao)
        
        return analise_df, correlacao