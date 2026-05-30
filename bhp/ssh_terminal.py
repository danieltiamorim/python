import paramiko
import getpass

def ssh_terminal(ip, port, user, passwd):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        # 1. Estabelece a conexão UMA única vez
        print(f"[*] Conectando a {ip}:{port}...")
        client.connect(ip, port=port, username=user, password=passwd)
        print("[+] Conectado com sucesso!")
        print("[*] Digite 'exit' para encerrar a sessão.\n")
        
        # 2. Entra no loop infinito de comandos
        while True:
            cmd = input(f"{user}@{ip} $> ")
            
            # Condição de saída
            if cmd.lower() == 'exit':
                print("[*] Fechando conexão...")
                break
                
            # Ignora se o usuário apertar Enter vazio
            if not cmd.strip():
                continue
                
            # 3. Executa o comando no servidor remoto
            stdin, stdout, stderr = client.exec_command(cmd)
            
            # 4. Lê a saída e os erros
            saida = stdout.read().decode('utf-8', errors='ignore').strip()
            erro = stderr.read().decode('utf-8', errors='ignore').strip()
            
            if saida:
                print(saida)
            if erro:
                print(f"Erro: {erro}")
                
    except Exception as e:
        print(f"[-] Ocorreu um erro: {e}")
    finally:
        client.close()

if __name__ == '__main__':
    user = input('Username: ')
    password = getpass.getpass('Password: ')
    
    ip = input('Insira o IP do Servidor (ex: 127.0.0.1): ') or '127.0.0.1'
    port = input('Insira a porta (Enter para 22): ')
    port = int(port) if port else 22
    
    ssh_terminal(ip, port, user, password)
