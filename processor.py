import os
import zipfile
import glob
import pandas as pd
import numpy as np

class DataProcessor:
    def __init__(self, data_dir="dados_tse"):
        self.data_dir = data_dir

    def _get_csv_from_zip(self, zip_path, pattern=".csv"):
        """Retorna o nome do arquivo dentro do ZIP que casa com o padrão."""
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for name in zf.namelist():
                if name.endswith(pattern) and "leiame" not in name.lower():
                    return name
        return None

    def process_eleitorado_infraestrutura(self, output_file="tabela_eleitorado_infra_2024.csv"):
        """
        Gera tabela agrupada por UF, Município com zonas, locais, seções e eleitorado.
        """
        print("Iniciando processamento do eleitorado e infraestrutura (2024)...")
        
        # 1. Obter mapeamento de seções para locais de votação
        locais_zip = os.path.join(self.data_dir, "eleitorado_local_votacao_2024.zip")
        if not os.path.exists(locais_zip):
            print(f"Arquivo não encontrado: {locais_zip}")
            return None
            
        csv_name = self._get_csv_from_zip(locais_zip)
        df_locais = None
        if csv_name:
            print("Carregando locais de votação...")
            with zipfile.ZipFile(locais_zip, 'r') as zf:
                with zf.open(csv_name) as f:
                    # Carregar apenas as colunas essenciais
                    cols = ['SG_UF', 'CD_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'NR_LOCAL_VOTACAO']
                    dtypes = {'SG_UF': 'category', 'CD_MUNICIPIO': 'int32', 
                              'NR_ZONA': 'int32', 'NR_SECAO': 'int32', 'NR_LOCAL_VOTACAO': 'int32'}
                    df_locais = pd.read_csv(f, sep=';', encoding='latin-1', usecols=cols, dtype=dtypes)
        else:
            print("CSV de locais de votação não encontrado no ZIP.")
            return None

        # 2. Processar arquivos estaduais de perfil do eleitor
        perfil_files = glob.glob(os.path.join(self.data_dir, "perfil_eleitor_secao_2024_[A-Z][A-Z].zip"))
        
        lista_agregados = []
        # Lista para armazenar dados por UF antes do merge
        
        for p_file in perfil_files:
            csv_name = self._get_csv_from_zip(p_file)
            if not csv_name:
                continue
                
            print(f"Processando {os.path.basename(p_file)}...")
            with zipfile.ZipFile(p_file, 'r') as zf:
                with zf.open(csv_name) as f:
                    cols = ['SG_UF', 'CD_MUNICIPIO', 'NM_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'DS_GENERO', 'QT_ELEITORES_PERFIL']
                    dtypes = {
                        'SG_UF': 'category',
                        'CD_MUNICIPIO': 'int32',
                        'NM_MUNICIPIO': 'category',
                        'NR_ZONA': 'int32',
                        'NR_SECAO': 'int32',
                        'DS_GENERO': 'category',
                        'QT_ELEITORES_PERFIL': 'int32'
                    }
                    
                    df_uf = pd.read_csv(f, sep=';', encoding='latin-1', usecols=cols, dtype=dtypes)
                    
                    # Agrupar por seção considerando gênero
                    # Pivot para ter colunas FEMININO e MASCULINO
                    df_pivot = df_uf.pivot_table(
                        index=['SG_UF', 'CD_MUNICIPIO', 'NM_MUNICIPIO', 'NR_ZONA', 'NR_SECAO'],
                        columns='DS_GENERO',
                        values='QT_ELEITORES_PERFIL',
                        aggfunc='sum',
                        fill_value=0,
                        observed=True
                    ).reset_index()

                    # Limpar nomes de colunas
                    df_pivot.columns.name = None
                    
                    # Somar total
                    if 'MASCULINO' not in df_pivot: df_pivot['MASCULINO'] = 0
                    if 'FEMININO' not in df_pivot: df_pivot['FEMININO'] = 0
                    
                    df_pivot['TOTAL'] = df_pivot['MASCULINO'] + df_pivot['FEMININO']
                    # Adicionar não informados se houver outras categorias e depois somar tudo no total geral
                    # Mas para o exercício vamos somar todas as numéricas no Total
                    all_genders = [c for c in df_pivot.columns if c not in ['SG_UF', 'CD_MUNICIPIO', 'NM_MUNICIPIO', 'NR_ZONA', 'NR_SECAO', 'MASCULINO', 'FEMININO', 'TOTAL']]
                    df_pivot['TOTAL'] += df_pivot[all_genders].sum(axis=1) if len(all_genders) > 0 else 0
                    
                    # Fazer merge com locais
                    df_merged = pd.merge(df_pivot, df_locais, on=['SG_UF', 'CD_MUNICIPIO', 'NR_ZONA', 'NR_SECAO'], how='left')
                    lista_agregados.append(df_merged)

        # Junta todos os estados
        if not lista_agregados:
            print("Nenhum dado estadual de perfil processado.")
            return None
            
        df_completo = pd.concat(lista_agregados, ignore_index=True)
        
        # 3. Agrupar por município
        print("Agregando resultados finais por município...")
        
        # A unicidade das entidades conforme regra de negócio
        # Zonas: UF + Zona
        # Local: UF + Zona + Município + Local
        # Seção: UF + Zona + Seção
        
        # Criar ids únicos para a contagem
        df_completo['UID_ZONA'] = df_completo['SG_UF'].astype(str) + "_" + df_completo['NR_ZONA'].astype(str)
        df_completo['UID_SECAO'] = df_completo['UID_ZONA'] + "_" + df_completo['NR_SECAO'].astype(str)
        
        # Tratamento para NaN no NR_LOCAL_VOTACAO via merge
        df_completo['NR_LOCAL_VOTACAO'] = df_completo['NR_LOCAL_VOTACAO'].fillna(-1).astype(int)
        df_completo['UID_LOCAL'] = df_completo['UID_ZONA'] + "_" + df_completo['CD_MUNICIPIO'].astype(str) + "_" + df_completo['NR_LOCAL_VOTACAO'].astype(str)

        # Agrupar por Município
        agg_cols = {
            'UID_ZONA': 'nunique',
            'UID_LOCAL': 'nunique',
            'UID_SECAO': 'nunique',
            'TOTAL': 'sum',
            'FEMININO': 'sum',
            'MASCULINO': 'sum'
        }
        
        df_final = df_completo.groupby(['SG_UF', 'NM_MUNICIPIO'], as_index=False).agg(agg_cols)
        
        df_final.rename(columns={
            'UID_ZONA': 'NUM_ZONAS',
            'UID_LOCAL': 'NUM_LOCAIS_VOTACAO',
            'UID_SECAO': 'NUM_SECOES',
            'TOTAL': 'ELEITORADO_TOTAL',
            'FEMININO': 'ELEITORADO_FEMININO',
            'MASCULINO': 'ELEITORADO_MASCULINO'
        }, inplace=True)
        
        # Porcentagens
        df_final['PCT_FEMININO'] = np.where(df_final['ELEITORADO_TOTAL'] > 0, (df_final['ELEITORADO_FEMININO'] / df_final['ELEITORADO_TOTAL']) * 100, 0)
        df_final['PCT_MASCULINO'] = np.where(df_final['ELEITORADO_TOTAL'] > 0, (df_final['ELEITORADO_MASCULINO'] / df_final['ELEITORADO_TOTAL']) * 100, 0)
        
        # Salvar o csv final
        df_final.to_csv(output_file, index=False, sep=';', encoding='latin-1')
        print(f"Processamento concluído. Salvo em: {output_file}")
        return output_file

if __name__ == "__main__":
    processor = DataProcessor()
    processor.process_eleitorado_infraestrutura()
