import socket
target_host = "127.0.0.1"
target_port = 9997

#criar um objeto socket
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#enviar alguns dados
client.sendto(b"AAABBBCCC",(target_host,target_port))

#receber alguns dados
data, addr = client.recvfrom(4096)

print(data.decode())
client.close() 