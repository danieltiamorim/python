nome_completo =  "Daniel H. Amorim "
nome_completo_aspas = '''Daniel H. Amorim'''
nome_completo_quebra = "Daniel\nH.\nAmorim"
nome_completo_quebra2 = """Daniel
H.
Amorim"""
nome = "Daniel"
sobrenome = "H. Amorim "

print ("Nome completo (1ª Forma):", nome_completo)
print ("Nome completo (2ª Forma): "+ nome_completo)
print ("Nome completo (3ª Forma): "+ "Daniel " + "H. " +"Amorim")
print ("Nome completo (4ª Forma): "+ "Daniel", "H. " + "Amorim")
print ("Nome completo (5ª Forma):", nome_completo_aspas)
print ("Nome completo (6ª Forma):", nome_completo_quebra)
print ("Nome completo (7ª Forma): {}".format(nome_completo))
print ("Nome completo (8ª Forma): {} {}".format(nome, sobrenome))
print ("Nome completo (9ª Forma): %s %s" %(nome, sobrenome))
print ("Nome completo (10ª Forma): %s" %nome_completo)
print ("Nome completo (11ª Forma):", nome_completo_quebra2)
print ("Nome repetido duas vezes:", nome_completo * 2)
