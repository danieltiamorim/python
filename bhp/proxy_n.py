import sys
import socket
import threading


HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range (256)])

def hexdump(src, length=16, show=True):
    if isinstance(src, bytes):
        src = src.decode()

    results = list()
    for i in range(0, len(src), length):
        word = str(src[i:i+length])

        printable = word.translate(HEX_FILTER)
        hexa = ' '.join([f'{ord(c):02X}' for c in word])
        hexwidth = length*3
        results.append(f'{i:04x} {hexa:<{hexwidth}} {printable}')
    if show:
        for line in results:
            print(line)
    else:
        return results
        

def receive_from(connection):
    buffer = b""
    # Timeout inicial: aguarda até 5s para o servidor COMEÇAR a responder
    connection.settimeout(5)
    
    try:
        while True:
            data = connection.recv(4096)
            if not data:
                # Se o buffer ainda estiver vazio e não recebermos dados,
                # significa que a conexão fechou, não é só uma pausa.
                if not buffer:
                    return None 
                break
            buffer += data
            # Se já pegamos dados, diminuimos o timeout para ser ágil
            connection.settimeout(0.5)
            
    except socket.timeout:
        # Timeout é normal, apenas retorna o que lemos (mesmo que seja nada)
        pass
    except Exception as e:
        # Qualquer outro erro, assumimos que a conexão morreu
        return None
        
    return buffer


def request_handler(buffer):
    #realizar modificações no pacote 
    return buffer

def response_handler(buffer):
    #realizar modificações no pacote
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        remote_socket.connect((remote_host, remote_port))
    except:
        print("[!!] Falha ao conectar ao servidor remoto.")
        client_socket.close()
        return

    # Buffer inicial (se necessário)
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        if remote_buffer:
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            if len(remote_buffer):
                client_socket.send(remote_buffer)

    while True:
        # 1. LER DO LOCALHOST
        local_buffer = receive_from(client_socket)
        
        # Se recebeu None, a conexão morreu. Break.
        if local_buffer is None: 
            break

        if len(local_buffer):
            line = "[==>] Recebido %d bytes de localhost." % len(local_buffer)
            print(line)
            hexdump(local_buffer)
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Enviado para o Servidor remoto.")

        # 2. LER DO REMOTO
        remote_buffer = receive_from(remote_socket)

        # Se recebeu None, a conexão morreu. Break.
        if remote_buffer is None:
            break

        if len(remote_buffer):
            print("[<==] Recebido %d bytes do Servidor Remoto." % len(remote_buffer))
            hexdump(remote_buffer)
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
            print("[<==] Enviado para o localhost.")

        # Removemos o "if not len or not len" antigo.
        # O loop agora só quebra se receber None (socket fechado).

    client_socket.close()
    remote_socket.close()
    print("[*] Não há mais dados. Fechando Conexões.")

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print('problema ao conectar: %r' % e)
        
        print("[!!] Falha ao ouvir em %s:%d" % (local_host, local_port))
        print("[!!] Verifique outros sockets de escuta ou corrija as permissões.")
        sys.exit(0)

    print("[*] Ouvindo em %s:%d" % (local_host, local_port))
   #'server.listen(5)' para respostas e tempo de espera mais rápidas, se for necessário mais tempo, pode aumentar esse número. 
    server.listen(5)
    while True:
        client_socket, addr = server.accept()
        #imprimir as informações da conexão local
        line = "> Conexão de entrada recebida de %s:%d" % (addr[0], addr[1])
        print(line)
        #iniciar uma thread para se comunicar com o host remoto
        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first))
        proxy_thread.start()

def main():
    if len(sys.argv[1:]) !=5:
        print("Uso: ./proxy.py [localhost] [localport])", end='')
        print("[remote host] [remote_port] [receive_first]")
        print("Exemplo: ./proxy.py 127.0.0.1 9000 10.12.132.1 9000 True")
        sys.exit(0)
    local_host =  sys.argv[1]
    local_port =  int(sys.argv[2])

    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()
