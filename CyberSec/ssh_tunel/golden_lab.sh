#### Script: golden_server.py
# Este script é um servidor SSH personalizado que aceita conexões de clientes e permite que eles criem túneis dinâmicos (Dynamic Port Forwarding) 
# para qualquer destino que desejarem. Ele utiliza a biblioteca Paramiko para criar um servidor SSH e aceitar conexões.
# O servidor escuta na porta 2223 e, quando um cliente se conecta, ele aceita a sessão e aguarda pedidos de túneis dinâmicos.
# Quando um cliente solicita um túnel para um destino específico, o servidor cria uma conexão TCP para esse destino e redireciona 
# o tráfego entre o cliente e o destino solicitado.
# Para testar, primeiro execute este script para iniciar o servidor, e depois configure um cliente SSH (como o OpenSSH) para usar 
# este servidor como um proxy SOCKS5, ou use um cliente personalizado que suporte túneis dinâmicos para se conectar ao servidor e criar 
# túneis para destinos de sua escolha.

cat << 'EOF' > golden_server.py
import socket
import paramiko
import threading
import sys
import select

HOSTKEY = paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
        # DICIONÁRIO DE MEMÓRIA: Guarda os destinos que os clientes pedem
        self.requested_destinations = {} 

    def check_channel_direct_tcpip_request(self, chanid, origin, destination):
        print(f"[DEBUG] Cliente pediu túnel dinâmico para: {destination[0]}:{destination[1]}")
        # Salva o destino associado ao ID deste canal específico
        self.requested_destinations[chanid] = destination
        return paramiko.OPEN_SUCCEEDED

    def check_channel_request(self, kind, chanid):
        if kind == 'session': return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_auth_password(self, username, password):
        if (username == 'daniel') and (password == 'password'): return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

# Agora a função recebe o host e a porta dinamicamente
def tunnel_handler(chan, dest_host, dest_port):
    sock = socket.socket()
    try:
        print(f"[*] Conectando ao alvo solicitado: {dest_host}:{dest_port}...")
        sock.connect((dest_host, dest_port))
    except Exception as e:
        print(f"[-] Erro ao conectar no alvo dinâmico: {e}")
        chan.close()
        return

    print(f"[+] Túnel Operante! Transferindo dados...")
    
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
    print("[*] Conexão fechada.")

def start_server():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('0.0.0.0', 2223))
        sock.listen(100)
        print("[+] C2 Dinâmico ouvindo na porta 2223...")
        
        client, addr = sock.accept()
        print(f"[+] Conexão de {addr}")
        
        t = paramiko.Transport(client)
        t.add_server_key(HOSTKEY)
        server = Server()
        t.start_server(server=server)
        
        while True:
            chan = t.accept(20)
            if chan is None: continue
            
            chanid = chan.get_id()
            
            # Verifica se é um canal de túnel que salvamos na memória
            if chanid in server.requested_destinations:
                dest_host, dest_port = server.requested_destinations[chanid]
                print(f"[DEBUG] Canal {chanid} aceito! Redirecionando tráfego para {dest_host}:{dest_port}")
                
                thr = threading.Thread(target=tunnel_handler, args=(chan, dest_host, dest_port))
                thr.daemon = True
                thr.start()
                
                # Limpa a memória para não vazar RAM com o tempo
                del server.requested_destinations[chanid]
            else:
                chan.close()
                
    except KeyboardInterrupt: sys.exit(0)
    except Exception as e: print(f"[ERRO] {e}")

if __name__ == "__main__":
    start_server()
EOF