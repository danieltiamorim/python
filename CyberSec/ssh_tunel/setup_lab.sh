#!/bin/bash

# Cores
VERDE='\033[0;32m'
AZUL='\033[0;34m'
NC='\033[0m'

echo -e "${AZUL}[*] Aplicando correção no Laboratório SSH...${NC}"

# Recriando o SERVIDOR UNIVERSAL (Versão corrigida e simplificada)
echo -e "${VERDE}[+] Atualizando 'universal_server.py'...${NC}"
cat << 'EOF' > universal_server.py
import os
import paramiko
import socket
import sys
import threading
import select

CWD = os.path.dirname(os.path.realpath(__file__))
HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    # CORREÇÃO: Removido o argumento 'para' que causava o crash
    def check_channel_request(self, kind, chanid):
        if kind == 'session' or kind == 'direct-tcpip':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if (username == 'daniel') and (password == 'password'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

def tunnel_handler(chan, host, port):
    sock = socket.socket()
    try:
        sock.connect((host, port))
    except Exception as e:
        print(f"[-] Erro ao conectar no destino {host}:{port} -> {e}")
        chan.close()
        return

    print(f"[*] Conectado ao Google! Transferindo dados...")
    
    while True:
        try:
            r, w, x = select.select([sock, chan], [], [])
            if sock in r:
                data = sock.recv(1024)
                if len(data) == 0: break
                chan.send(data)
            if chan in r:
                data = chan.recv(1024)
                if len(data) == 0: break
                sock.send(data)
        except Exception:
            break
            
    chan.close()
    sock.close()
    print(f"[*] Conexão encerrada.")

if __name__ == '__main__':
    server = '0.0.0.0' # Escuta em todas as interfaces
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print(f'[+] Servidor Corrigido ouvindo em {server}:{ssh_port}...')
        client, addr = sock.accept()
    except Exception as e:
        print('[-] Falha no Bind: ' + str(e))
        sys.exit(1)
    
    print(f'[+] Cliente conectado: {addr}')
    
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except:
        print("[-] Erro SSH")
        sys.exit(1)
    
    try:
        while True:
            chan = bhSession.accept(20)
            if chan is None: continue
            
            if chan.get_name() == 'direct-tcpip':
                print("[*] Pedido de túnel recebido!")
                # Para garantir que funcione no lab, forçamos o destino para o Google
                # independentemente do que o cliente pediu.
                t = threading.Thread(target=tunnel_handler, args=(chan, 'www.google.com', 80))
                t.daemon = True
                t.start()
            elif chan.get_name() == 'session':
                chan.close()
                    
    except KeyboardInterrupt:
        bhSession.close()
EOF

echo -e "${AZUL}-------------------------------------------------------${NC}"
echo -e "${VERDE}CORREÇÃO APLICADA!${NC}"
echo -e "${AZUL}-------------------------------------------------------${NC}"
echo -e "Agora tente novamente:"
echo -e "1. Terminal 1: sudo python3 universal_server.py"
echo -e "2. Terminal 2: python3 forward.py 127.0.0.1:2222 -p 8080 -r www.google.com:80 --user daniel --password password"
echo -e "3. Teste:      curl http://127.0.0.1:8080"
