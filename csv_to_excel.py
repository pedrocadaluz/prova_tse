import os
import glob
import pandas as pd

def converter_csv_para_excel():
    print("Iniciando conversão de arquivos CSV para Excel (XLSX)...")
    
    # Busca por todos os arquivos CSV gerados na pasta raiz do projeto
    csv_files = glob.glob("*.csv")
    
    if not csv_files:
        print("Nenhum arquivo CSV encontrado na pasta atual.")
        return

    for csv_file in csv_files:
        excel_file = csv_file.replace('.csv', '.xlsx')
        print(f"Lendo {csv_file}...")
        
        try:
            # Lendo com o padrão do nosso projeto (; e latin-1)
            df = pd.read_csv(csv_file, sep=';', encoding='latin-1')
            
            print(f"Salvando como {excel_file}...")
            # to_excel requer a biblioteca openpyxl
            df.to_excel(excel_file, index=False, engine='openpyxl')
            print(f"[OK] {excel_file} gerado com sucesso!")
            
        except Exception as e:
            print(f"[ERRO] Falha ao converter {csv_file}: {e}")

if __name__ == "__main__":
    converter_csv_para_excel()
