import os
import paramiko
import socket
import sys
import threading

CWD = os.path.dirname(os.path.realpath(__file__))

#se o parâmetro HOSTKEY não funcionar, talvez seja necessário gerar uma chave rsa,
#pra isso é só rodar o comando abaixo.
#ssh-keygen -t rsa -f test_rsa.key -N ""

HOSTKEY = paramiko.RSAKey(filename=os.path.join(CWD, 'test_rsa.key'))

class Server (paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        
    def check_channel_request(self, kind, chanid):
        if kind == 'session' or kind == 'direct-tcpip':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    
    def check_auth_password(self, username, password):
        if (username == 'daniel') and (password == 'password'):
            return paramiko.AUTH_SUCCESSFUL
        
    def check_port_forward_request(self, address, port):
        # Retorna True para dizer "Sim, eu permito encaminhar portas"
        print(f"[*] Pedido de encaminhamento recebido para {address}:{port}")
        return True
    
    
        
if __name__ == '__main__':
    server = '0.0.0.0'
    ssh_port = 2222
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((server, ssh_port))
        sock.listen(100)
        print('[+] Ouvindo conexões... ')
        client, addr = sock.accept ()
    except Exception as e:
        print('[-] Falha na Escuta: ' + str(e))
        sys.exit(1)
    else:
        print('[+] Conexão Estabelecida!', client, addr)
        
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(HOSTKEY)
    server = Server()
    bhSession.start_server(server=server)
    
    # O servidor espera 20 segundos por um shell/comando
    chan = bhSession.accept(20)

    if chan is None:
        print('*** Sem canal Interativo (Shell). Mantendo túnel ativo... ***')
        # NÃO FAÇA sys.exit(1) AQUI se quiser manter o túnel (rforward)
        # Vamos criar um loop infinito para manter o script rodando
        # enquanto o paramiko gerencia o túnel em outra thread.
        import time
        try:
            while bhSession.is_active(): 
                time.sleep(1)
        except KeyboardInterrupt:
            bhSession.close()
        sys.exit(0)

    # Se chegou aqui, é porque existe um canal (chan) de comando
    print('[+] Autenticado!')
    print(chan.recv(1024))
    chan.send('Bem-vindo ao bh_ssh')
    
    try:
        while True:
            command= input("Insira o comando: ")
            if command != 'exit':
                chan.send(command)
                r = chan.recv(8192)
                print(r.decode('utf-8', errors='ignore'))
            else:
                chan.send('exit')
                print('exiting')
                bhSession.close()
                break
    except KeyboardInterrupt:
        bhSession.close()