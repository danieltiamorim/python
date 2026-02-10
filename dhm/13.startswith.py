nome = input("Insira um nome aqui: ")
inicio = input("Insira um texto do INICIO aqui: ")
fim = input("Insira um texto do FIM nome aqui: ")

resultado = nome.startswith(inicio) 

if resultado:
    # Isso é o mesmo que 'if resultado == True:'
    print("Verdadeiro, o nome INICIA com essas palavras")
else:
    print("Falso, o nome NÃO INICIA com essas palavras.")


resultado = (nome.endswith(fim))

if resultado:
    # Isso é o mesmo que 'if resultado == True:'
    print("Verdadeiro, o nome FINALIZA com essa palavra")
else:
    print("Falso, o nome NÃO FINALIZA com essa palavra")