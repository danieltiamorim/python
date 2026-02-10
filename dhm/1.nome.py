nome = input("Escreva seu nome: ")
sobrenome = input("Escreva seu sobrenome: ")
idade = (int(input("Escreva sua idade: ")))
print ("Seu nome é", nome, sobrenome)
print ("Você tem", idade, "ano(s)")
adolescente = (13 - idade)
adulto = (18 - idade)
idoso = (75 - idade)

if (idade < 13):
    print ("Você é uma Criança")
    
elif (idade >= 13 and idade < 18):
    print ("Você é um(a) Adolescente")   
    print ("Faltam", adulto, "ano(s) para a fase adulta" )

elif (idade >= 18 and idade < 30):
    print ("Você já é um(a) Adulto(a)")

elif (idade > 30  and idade < 75):
    print ("Tá ficando velho")
    print ("Faltam", idoso, "ano(s) para a fase idoso(a)" )

elif (idade >= 75):
    print ("Parabéns! Você é um idoso, está na melhor idade e passou de todas as fases!")