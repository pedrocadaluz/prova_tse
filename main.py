import argparse
import sys
from pathlib import Path

from src.downloader import DataDownloader
from src.processor import DataProcessor
from src.analyzer import DataAnalyzer
from src.visualizer import generate_mapa_deficiencia, plotar_serie_mulheres

def orquestrar(etapas=[]):
    BASE_DIR = Path(__file__).resolve().parent
    data_raw_dir = BASE_DIR / "data" / "raw"
    data_processed_dir = BASE_DIR / "data" / "processed"
    reports_dir = BASE_DIR / "reports"
    
    data_raw_dir.mkdir(parents=True, exist_ok=True)
    data_processed_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    if "1" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 1: Ingestão de Dados (Downloader) ===")
        downloader = DataDownloader(output_dir=data_raw_dir)
        downloader.run_all()
        
    if "2" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 2: Processamento (Tabela de Eleitorado e Infraestrutura) ===")
        processor = DataProcessor(data_dir=data_raw_dir, processed_dir=data_processed_dir)
        processor.process_eleitorado_infraestrutura()
        
    if "3" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 3: Análise e Visualização (Mapa de Deficiência 2024) ===")
        generate_mapa_deficiencia(data_dir=data_raw_dir, reports_dir=reports_dir)

    if "4" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 4: Análise (Prefeitos Eleitos nas Capitais 2024) ===")
        analyzer = DataAnalyzer(data_dir=data_raw_dir, processed_dir=data_processed_dir)
        analyzer.analisar_prefeitos_capitais_2024()
        
    if "5" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 5: Análise (Série Histórica de Mulheres Eleitas 2016-2024) ===")
        analyzer = DataAnalyzer(data_dir=data_raw_dir, processed_dir=data_processed_dir)
        analyzer.consolidar_serie_mulheres_eleitas()
        # Chama a visualização na mesma etapa
        plotar_serie_mulheres(processed_dir=data_processed_dir, reports_dir=reports_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline de Dados do TSE (Eleições Municipais)")
    parser.add_argument(
        '--etapas',
        nargs='+',
        default=['tudo'],
        help="Etapas do pipeline a executar: 1 2 3 4 5 ou 'tudo' (ex: --etapas 1 4)"
    )
    
    args = parser.parse_args()
    
    print(f"Executando pipeline para as etapas: {args.etapas}")
    try:
        if args.etapas == ['tudo']:
            etapas_exec = ["1", "2", "3", "4", "5"]
        else:
            etapas_exec = args.etapas
            
        orquestrar(etapas=etapas_exec)
        print("\n[SUCESSO] Pipeline finalizado com sucesso!")
    except Exception as e:
        print(f"\n[ERRO] Erro durante a execução do pipeline: {e}")
        sys.exit(1)
