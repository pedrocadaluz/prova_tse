import os
import zipfile
import pandas as pd
import unicodedata
from pathlib import Path

def remove_accents(input_str):
    if pd.isna(input_str):
        return input_str
    nfkd_form = unicodedata.normalize('NFKD', str(input_str))
    return u"".join([c for c in nfkd_form if not unicodedata.combining(c)]).upper()

class DataAnalyzer:
    def __init__(self, data_dir=None, processed_dir=None):
        base_dir = Path(__file__).resolve().parent.parent
        self.data_dir = Path(data_dir) if data_dir else base_dir / "data" / "raw"
        self.processed_dir = Path(processed_dir) if processed_dir else base_dir / "data" / "processed"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
        self.capitais = {
            "AC-RIO BRANCO", "AL-MACEIO", "AP-MACAPA", "AM-MANAUS", "BA-SALVADOR", "CE-FORTALEZA",
            "ES-VITORIA", "GO-GOIANIA", "MA-SAO LUIS", "MT-CUIABA", "MS-CAMPO GRANDE", "MG-BELO HORIZONTE",
            "PA-BELEM", "PB-JOAO PESSOA", "PR-CURITIBA", "PE-RECIFE", "PI-TERESINA", "RJ-RIO DE JANEIRO",
            "RN-NATAL", "RS-PORTO ALEGRE", "RO-PORTO VELHO", "RR-BOA VISTA", "SC-FLORIANOPOLIS",
            "SP-SAO PAULO", "SE-ARACAJU", "TO-PALMAS"
        }

    def _get_csv_from_zip(self, zip_path, pattern=".csv"):
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for name in zf.namelist():
                if name.endswith(pattern) and "leiame" not in name.lower():
                    return name
        return None

    def analisar_prefeitos_capitais_2024(self, output_file="prefeitos_capitais_2024.csv"):
        print("Analisando prefeitos eleitos nas capitais (2024)...")
        zip_path = self.data_dir / "consulta_cand_2024.zip"
        if not zip_path.exists():
            print(f"Arquivo não encontrado: {zip_path}")
            return None

        # O arquivo do TSE costuma se chamar consulta_cand_2024_BRASIL.csv
        # Vou procurar todos os CSVs iterativamente se separados por estado
        dfs = []
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Evitar arquivos consolidados do Brasil para não haver dupla contagem e poupar memória
            csv_files = [n for n in zf.namelist() if n.endswith('.csv') and "leiame" not in n.lower() and "brasil" not in n.lower() and not n.lower().endswith('_br.csv')]
            for csv_name in csv_files:
                with zf.open(csv_name) as f:
                    cols = ['SG_UF', 'DS_CARGO', 'NM_UE', 'NM_URNA_CANDIDATO', 'DS_SIT_TOT_TURNO']
                    # Usar read_csv com subset the cols, on error ignore
                    try:
                        df = pd.read_csv(f, sep=';', encoding='latin-1', usecols=lambda c: c in cols)
                        
                        # Filtrar apenas PREFEITO
                        df = df[df['DS_CARGO'] == 'PREFEITO']
                        
                        # Filtrar SITUACAO = ELEITO, ELEITO POR QP, ELEITO POR MEDIA
                        eleito_str = ['ELEITO', 'ELEITO POR QP', 'ELEITO POR MÉDIA', 'ELEITO POR MEDIA']
                        df = df[df['DS_SIT_TOT_TURNO'].isin(eleito_str)]
                        
                        # Remover acentos do nome do município
                        df['NM_MUNICIPIO_NORM'] = df['NM_UE'].apply(remove_accents)
                        
                        # Criar chave UF-MUNICIPIO para filtragem estrita
                        df['CHAVE_CAPITAL'] = df['SG_UF'] + "-" + df['NM_MUNICIPIO_NORM']
                        
                        # Filtrar capitais
                        df_caps = df[df['CHAVE_CAPITAL'].isin(self.capitais)]
                        if not df_caps.empty:
                            # Limpar colunas auxiliares para economizar memória
                            df_caps = df_caps.drop(columns=['NM_MUNICIPIO_NORM', 'CHAVE_CAPITAL'])
                            dfs.append(df_caps)
                    except ValueError as e:
                        # Pular se as colunas não existirem
                        pass

        if not dfs:
            print("Nenhum prefeito de capital encontrado nos dados lidos.")
            return None

        df_final = pd.concat(dfs, ignore_index=True)
        df_final = df_final.drop_duplicates(subset=['NM_UE', 'NM_URNA_CANDIDATO'])
        
        output_path = self.processed_dir / output_file
        df_final.to_csv(output_path, index=False, sep=';', encoding='latin-1')
        print(f"Resultado salvo em {output_path}")
        return df_final

    def consolidar_serie_mulheres_eleitas(self, output_file="serie_mulheres_eleitas.csv"):
        print("Consolidando série histórica de mulheres eleitas (2016-2024)...")
        anos = [2016, 2020, 2024]
        eleitos_por_ano = []

        eleito_str = ['ELEITO', 'ELEITO POR QP', 'ELEITO POR MÉDIA', 'ELEITO POR MEDIA']

        for ano in anos:
            zip_path = self.data_dir / f"consulta_cand_{ano}.zip"
            if not zip_path.exists():
                print(f"Arquivo pulado (não encontrado): {zip_path}")
                continue
            
            total_mulheres_eleitas = 0
            with zipfile.ZipFile(zip_path, 'r') as zf:
                # Evitar dupla contagem ignorando os arquivos consolidados do Brasil BRASIL/BR
                csv_files = [n for n in zf.namelist() if n.endswith('.csv') and "leiame" not in n.lower() and "brasil" not in n.lower() and not n.lower().endswith('_br.csv')]
                for csv_name in csv_files:
                    with zf.open(csv_name) as f:
                        cols = ['DS_GENERO', 'DS_SIT_TOT_TURNO']
                        try:
                            df = pd.read_csv(f, sep=';', encoding='latin-1', usecols=lambda c: c in cols)
                            mask = (df['DS_GENERO'].astype(str).str.upper() == 'FEMININO') & (df['DS_SIT_TOT_TURNO'].isin(eleito_str))
                            total_mulheres_eleitas += mask.sum()
                        except ValueError:
                            pass
            
            eleitos_por_ano.append({'ANO': ano, 'MULHERES_ELEITAS': total_mulheres_eleitas})
            print(f"Ano {ano}: {total_mulheres_eleitas} mulheres eleitas.")

        df_final = pd.DataFrame(eleitos_por_ano)
        output_path = self.processed_dir / output_file
        df_final.to_csv(output_path, index=False, sep=';', encoding='latin-1')
        print(f"Série consolidada e salva em {output_path}")
        return df_final

if __name__ == "__main__":
    analyzer = DataAnalyzer()
    analyzer.analisar_prefeitos_capitais_2024()
    analyzer.consolidar_serie_mulheres_eleitas()
