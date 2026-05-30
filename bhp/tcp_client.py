import socket
target_host = "127.0.0.1" 
target_port = 9998

#criar um objeto socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#conectar o cliente
client.connect((target_host,target_port))

#enviar alguns dados
client.send(b"GET / HTTP/1.1\r\n Host: servidor_falso.com\r\n User-Agent: Navegador Falso \r\n ABCDEF \r\n Y0uH4v3B33nPwn3d")

#receber alguns dados
response = client.recv(4096)

print(response.decode())
client.close()
