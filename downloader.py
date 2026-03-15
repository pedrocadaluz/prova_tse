import os
import re
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class DataDownloader:
    def __init__(self, output_dir="dados_tse"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
            
    def _get_zip_links(self, url, patterns):
        try:
            response = requests.get(url, verify=False, timeout=30)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Erro ao acessar {url}: {e}")
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if not href.endswith('.zip'):
                continue
            for pattern in patterns:
                if re.search(pattern, href):
                    links.append(href)
                    break
        return list(set(links))

    def _download_file(self, url):
        local_filename = os.path.join(self.output_dir, url.split('/')[-1])
        if os.path.exists(local_filename):
            print(f"[{local_filename}] já existe, ignorando download.")
            return local_filename
            
        print(f"Baixando {url} para {local_filename}...")
        try:
            with requests.get(url, stream=True, verify=False, timeout=60) as r:
                r.raise_for_status()
                with open(local_filename, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"Sucesso: {local_filename}")
        except Exception as e:
            print(f"Erro ao baixar {url}: {e}")
            if os.path.exists(local_filename):
                os.remove(local_filename)
        return local_filename

    def download_eleitorado_2024(self):
        url = "https://dadosabertos.tse.jus.br/dataset/eleitorado-2024"
        patterns = [
            r"perfil_eleitor_deficiencia_2024\.zip$",
            r"eleitorado_local_votacao_2024\.zip$",
            r"perfil_eleitor_secao_2024_[A-Z]{2}\.zip$"
        ]
        links = self._get_zip_links(url, patterns)
        for link in links:
            self._download_file(link)

    def download_candidatos_2016(self):
        url = "https://dadosabertos.tse.jus.br/dataset/candidatos-2016"
        patterns = [r"consulta_cand_2016\.zip$"]
        links = self._get_zip_links(url, patterns)
        for link in links:
            self._download_file(link)

    def download_candidatos_2020(self):
        url = "https://dadosabertos.tse.jus.br/dataset/candidatos-2020-subtemas"
        patterns = [r"consulta_cand_2020\.zip$"]
        links = self._get_zip_links(url, patterns)
        for link in links:
            self._download_file(link)

    def download_candidatos_2024(self):
        url = "https://dadosabertos.tse.jus.br/dataset/candidatos-2024"
        patterns = [r"consulta_cand_2024\.zip$"]
        links = self._get_zip_links(url, patterns)
        for link in links:
            self._download_file(link)

    def run_all(self):
        print("Iniciando downloads...")
        self.download_eleitorado_2024()
        self.download_candidatos_2016()
        self.download_candidatos_2020()
        self.download_candidatos_2024()
        print("Downloads concluídos.")

if __name__ == "__main__":
    downloader = DataDownloader()
    downloader.run_all()
