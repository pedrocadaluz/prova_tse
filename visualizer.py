import os
import zipfile
import pandas as pd
import json

def generate_mapa_deficiencia(data_dir="dados_tse", output_html="mapa_deficiencia_2024.html"):
    print("Gerando mapa de deficiência (2024)...")
    try:
        import plotly.express as px
    except ImportError:
        print("Aviso: 'plotly' não instalado. Instale usando 'pip install plotly'")
        return

    zip_path = os.path.join(data_dir, "perfil_eleitor_deficiencia_2024.zip")
    if not os.path.exists(zip_path):
        print(f"Arquivo não encontrado: {zip_path}")
        return
        
    dfs = []
    # Iterando pelos CSVs dentro do ZIP
    with zipfile.ZipFile(zip_path, 'r') as zf:
        csv_files = [n for n in zf.namelist() if n.endswith('.csv') and "leiame" not in n.lower()]
        for csv_name in csv_files:
            with zf.open(csv_name) as f:
                # O nome do arquivo zip original tem as colunas SG_UF e QT_ELEITORES_TIT_DEFICIENCIA (ou similar)
                # Vamos tentar ler todas e filtrar por regex / list comprehension
                cols_to_use = None
                
                # Ler a primeira linha do CSV para descobrir os nomes exatos das colunas
                head_df = pd.read_csv(f, sep=';', encoding='latin-1', nrows=1)
                col_uf = [c for c in head_df.columns if 'UF' in c.upper()][0] if any('UF' in c.upper() for c in head_df.columns) else 'SG_UF'
                col_qtde = [c for c in head_df.columns if 'QT_ELEITORES' in c.upper()][0] if any('QT_ELEITORES' in c.upper() for c in head_df.columns) else 'QT_ELEITORES_PERFIL_DEFICIENCIA'
                
                f.seek(0)
                
                try:
                    df = pd.read_csv(f, sep=';', encoding='latin-1', usecols=[col_uf])
                    df = df.rename(columns={col_uf: 'UF'})
                    df['TOTAL_DEFICIENCIA'] = 1
                    df_agg = df.groupby('UF', as_index=False)['TOTAL_DEFICIENCIA'].sum()
                    dfs.append(df_agg)
                except ValueError as e:
                    print(f"Ignorando arquivo {csv_name}: as colunas requeridas não existem ou houve um erro: {e}")

    if not dfs:
        print("Nenhum dado de deficiência lido.")
        return

    df_final = pd.concat(dfs, ignore_index=True)
    df_agrupado = df_final.groupby('UF', as_index=False)['TOTAL_DEFICIENCIA'].sum()

    # Gerar mapa (choropleth) 
    # Precisamos de um geojson do Brasil para plotar no plotly
    # Como não temos um geojson local, vamos usar uma versão simplificada built-in se existir ou baixar via urr/requests
    # Na ausência de geojson fácil do IBGE, podemos gerar um mapa de barras para evitar quebrar, mas vamos tentar choropleth usando as UFs como locations se Plotly aceitar implicitamente para Brasil, mas geralmente Plotly requer o GeoJSON para estados brasileiros.
    # Dado que estamos pedindo mapa choropleth, uma solução comum é usar 'locationmode' para paises, mas não para estados do BR nativamente.
    # Vamos importar um geojson da web dinamicamente.
    import urllib.request
    url_geojson = "https://raw.githubusercontent.com/codeforamerica/click_that_hood/master/public/data/brazil-states.geojson"
    try:
        with urllib.request.urlopen(url_geojson) as response:
            brasil_geojson = json.loads(response.read().decode())
        
        # O GeoJSON tem sigla do estado em `features[i]['properties']['sigla']`
        fig = px.choropleth(
            df_agrupado, 
            geojson=brasil_geojson, 
            locations='UF', 
            featureidkey="properties.sigla",
            color='TOTAL_DEFICIENCIA',
            color_continuous_scale="Blues",
            scope="south america",
            title="Eleitorado com Deficiência por UF - 2024",
            labels={'TOTAL_DEFICIENCIA': 'Qtd. Eleitores com Deficiência'}
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.write_html(output_html)
        print(f"Mapa salvo em {output_html}")
    except Exception as e:
        print(f"Não foi possível gerar o mapa coroplético devido à falta de acesso ao geojson: {e}")
        # Fallback para gráfico de barras
        fig = px.bar(df_agrupado, x='UF', y='TOTAL_DEFICIENCIA', title="Eleitores com Deficiência por UF - 2024")
        fig.write_html(output_html.replace('mapa', 'grafico_barras'))
        print(f"Fallback para gráfico de barras salvo: {output_html.replace('mapa', 'grafico_barras')}")

def plotar_serie_mulheres(input_file="serie_mulheres_eleitas.csv", output_html="serie_mulheres_eleitas.html"):
    print("Gerando gráfico da série histórica (2016-2024)...")
    try:
        import plotly.express as px
    except ImportError:
        print("Aviso: 'plotly' não instalado.")
        return

    if not os.path.exists(input_file):
        print(f"Arquivo não encontrado: {input_file}")
        return

    df = pd.read_csv(input_file, sep=';', encoding='latin-1')
    
    if df.empty:
        print("Os dados estão vazios. Nada a plotar.")
        return

    # Gráfico de Linha
    fig = px.line(
        df, 
        x="ANO", 
        y="MULHERES_ELEITAS", 
        title="Série Histórica: Mulheres Eleitas (2016 - 2024)",
        markers=True,
        labels={"ANO": "Ano da Eleição", "MULHERES_ELEITAS": "Total de Mulheres Eleitas"}
    )
    
    # Garantir que o eixo X mostre os anos inteiros
    fig.update_xaxes(type='category')
    fig.write_html(output_html)
    print(f"Gráfico de linha salvo em {output_html}")

if __name__ == "__main__":
    generate_mapa_deficiencia()
    plotar_serie_mulheres()
