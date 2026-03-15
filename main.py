import argparse
import sys

from downloader import DataDownloader
from processor import DataProcessor
from analyzer import DataAnalyzer
from visualizer import generate_mapa_deficiencia, plotar_serie_mulheres

def orquestrar(etapas=[]):
    data_dir = "dados_tse"
    
    if "1" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 1: Ingestão de Dados (Downloader) ===")
        downloader = DataDownloader(output_dir=data_dir)
        downloader.run_all()
        
    if "2" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 2: Processamento (Tabela de Eleitorado e Infraestrutura) ===")
        processor = DataProcessor(data_dir=data_dir)
        processor.process_eleitorado_infraestrutura()
        
    if "3" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 3: Análise e Visualização (Mapa de Deficiência 2024) ===")
        generate_mapa_deficiencia(data_dir=data_dir)

    if "4" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 4: Análise (Prefeitos Eleitos nas Capitais 2024) ===")
        analyzer = DataAnalyzer(data_dir=data_dir)
        analyzer.analisar_prefeitos_capitais_2024()
        
    if "5" in etapas or "tudo" in etapas:
        print("\n=== MÓDULO 5: Análise (Série Histórica de Mulheres Eleitas 2016-2024) ===")
        analyzer = DataAnalyzer(data_dir=data_dir)
        analyzer.consolidar_serie_mulheres_eleitas()
        # Chama a visualização na mesma etapa
        plotar_serie_mulheres()

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
