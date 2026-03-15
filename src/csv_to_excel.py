import pandas as pd
from pathlib import Path

def converter_csv_para_excel(processed_dir=None):
    print("Iniciando conversão de arquivos CSV para Excel (XLSX)...")
    
    if processed_dir is None:
        processed_dir = Path(__file__).resolve().parent.parent / "data" / "processed"
    else:
        processed_dir = Path(processed_dir)
        
    if not processed_dir.exists():
        print(f"Diretório não encontrado: {processed_dir}")
        return

    csv_files = list(processed_dir.glob("*.csv"))
    
    if not csv_files:
        print(f"Nenhum arquivo CSV encontrado em {processed_dir}.")
        return

    for csv_file in csv_files:
        excel_file = csv_file.with_suffix('.xlsx')
        print(f"Lendo {csv_file}...")
        
        try:
            # Lendo com o padrão do nosso projeto (; e latin-1)
            df = pd.read_csv(csv_file, sep=';', encoding='latin-1')
            
            print(f"Salvando como {excel_file}...")
            # to_excel requer a biblioteca openpyxl
            df.to_excel(excel_file, index=False, engine='openpyxl')
            print(f"[OK] {excel_file.name} gerado com sucesso!")
            
        except Exception as e:
            print(f"[ERRO] Falha ao converter {csv_file.name}: {e}")

if __name__ == "__main__":
    converter_csv_para_excel()
