import base64
print("\n Exercício sobre Codificação e Criptografia")

senha = input("Escreva sua senha: ")

codificado = base64.b64encode(senha.encode("utf-8"))
decodificado = base64.b64decode(codificado.decode("utf-8"))

print("\n Codificado em base64: ", codificado) 
print("Decodificado em base64, como string:", decodificado.decode("utf-8"))



print("\n Encriptada em HASH MD5 ")
import hashlib
def gerar_hash_md5(texto):
    hash_md5 = hashlib.md5()
    hash_md5.update(texto.encode("utf-8"))
# Retorna o hash em formato hexadecimal
    return hash_md5.hexdigest()

# Exemplo de uso
texto = senha
hash_md5 = gerar_hash_md5(texto)
print("Hash MD5: ", hash_md5)

print("\n Encriptada em HASH SHA256:")
def gerar_hash_sha256(texto):
    hash_sha256 = hashlib.sha256()
    hash_sha256.update(texto.encode("utf-8"))
    
# Retorna o hash em formato hexadecimal
    return hash_sha256.hexdigest()

# Exemplo de uso
texto = senha
hash_sha256 = gerar_hash_sha256(texto)
print("Hash SHA256:", hash_sha256)


from cryptography.fernet import Fernet

def encrypt(message, key):
    #Encripta uma mensagem usando AES.
    f = Fernet(key)
    encrypted = f.encrypt(message.encode())
    return encrypted

def decrypt(encrypted, key):
    #Decripta uma mensagem usando AES.
    f = Fernet(key)
    decrypted = f.decrypt(encrypted)
    return decrypted.decode()

# Gerando uma chave aleatória
key = Fernet.generate_key()

# Mensagem a ser encriptada
message = senha

# Encriptando a mensagem
encrypted_message = encrypt(message, key)
print("\n Mensagem Encriptada usando AES: \n", encrypted_message)
print("Chave Aleatória: \n",key)
# Decriptando a mensagem
decrypted_message = decrypt(encrypted_message, key)

print("\n Texto descriptografado: \n",decrypted_message) 