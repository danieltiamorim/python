nome = input("Escreva um nome: ")
sobrenome= input("Escreva um sobrenome: ")
print("\n Seu nome é ", nome,sobrenome)

nomecompleto=(nome+sobrenome)

novo = input("Escreva um novo SOBRENOME: ")

print("Substituindo para um novo sobrenome", nomecompleto.replace(sobrenome,novo))
print("\n Masss quando você pede para mostrar a variável novamente, ela trás a antiga: ",sobrenome)