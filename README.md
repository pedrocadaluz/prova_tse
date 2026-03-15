# TSE Data Pipeline

Este é um projeto de Engenharia e Análise de Dados em Python para extração, processamento, análise e visualização de dados abertos do TSE (Tribunal Superior Eleitoral), com foco nas eleições municipais.

O pipeline é modular, sendo responsável por ingerir grandes volumes de dados de forma automatizada (baixando arquivos `.zip` do TSE), cruzar e limpar bases de dados de eleitorado, locais de votação e candidatos, e gerar análises ricas através de arquivos consolidados (em `.csv` e `.xlsx`) bem como visualizações interativas (`.html`).

O orquestrador do projeto está concentrado no arquivo `main.py`, que gerencia cinco diferentes módulos:
1. **Módulo 1:** Ingestão de Dados (Downloader das bases do TSE de 2016, 2020 e 2024).
2. **Módulo 2:** Processamento (Cruzamento de tabelas de Infraestrutura e Eleitorado por Município/Estado).
3. **Módulo 3:** Visualização do Mapa de Deficiência (2024).
4. **Módulo 4:** Análise dos Prefeitos Eleitos nas Capitais (2024).
5. **Módulo 5:** Consolidação e Visualização da Série Histórica de Mulheres Eleitas (2016 a 2024).

---

## 🚀 Gerenciamento de Ambiente Virtual (uv)

Este projeto utiliza o **[uv](https://github.com/astral-sh/uv)** (um gerenciador de pacotes ultra-rápido escrito em Rust) para criar e gerenciar o ambiente virtual (`.venv`) e resolver todas as dependências mapeadas no `pyproject.toml` e no `uv.lock`. O objetivo do `uv` é garantir que qualquer pessoa que clone este projeto tenha exatamente as mesmas bibliotecas e as mesmas versões instaladas, sem instabilidades e numa fração de segundo.

### Como configurar e executar o projeto

Certifique-se de que você tenha o Python (versão 3.13 ou superior recomendada) e o `uv` instalados na sua máquina. 

**Passo 1: Instale o `uv` (caso ainda não possua)**
No Windows (usando PowerShell):
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```
Ou no macOS/Linux:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Passo 2: Clonar o repositório e acessar a pasta**
```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd tse_master
```

**Passo 3: Sincronizar as dependências e criar o `.venv`**
Execute o comando abaixo. O `uv` criará o ambiente virtual automaticamente no diretório `.venv` e instalará `pandas`, `plotly`, `kaleido`, `requests`, `beautifulsoup4`, e demais pacotes essenciais do projeto.
```bash
uv sync
```

**Passo 4: Executar o Pipeline Principal**
Em vez de ativar o `.venv` manualmente (apesar de ser possível usando `.venv\Scripts\activate`), basta utilizar o prefixo `uv run` para garantir que seu código está usando o ambiente virtual gerenciado.

Para orquestrar e rodar todo o pipeline de ponta a ponta (as 5 etapas sequencialmente):
```bash
uv run python main.py --etapas tudo
```

Se desejar executar apenas uma ou mais partes específicas (exemplo, apenas a análise de prefeitos de capitais e geração da série de mulheres eleitas):
```bash
uv run python main.py --etapas 4 5
```

---

## Estrutura do Projeto

O repositório é arquitetado seguindo boas práticas profissionais, priorizando a dinamicidade de caminhos absolutos baseados na raiz:
- `data/raw/`: Armazena os arquivos nativos e brutos transferidos online (.zip). 
- `data/processed/`: Tabelas cruzadas e limpas prontas para uso final do usuário (.csv e .xlsx). 
- `reports/`: Mapas gerados via Plotly e visões gráficas interativas em formato HTML e imagens estáticas de alta resolução em formato PNG (geradas via motor Kaleido).
- `src/`: Core do projeto contendo downloaders, analyzers, e processadores encapsulados em OOP limpo.
- `main.py`: O orquestrador via CLI (etapas `1 2 3 4 5`).
