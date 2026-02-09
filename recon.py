import argparse        
import sys

target = None
port = None

class Recon:
    def __init__(self, args):
        self.args = args
        self.port = port         
        self.target = target

    def run(self):
        if self.args.target != None and self.args.port != None:
            match self.args.port:
                case 80 | 8080 | 443 | 9443 | 8443 | 8888 | 8090:
                    print("\n recon.py ---> Detectando Serviço Web")
                case 22 | 23 | 3389:
                    print("\n recon.py ---> Detectando Serviço de Acesso Remoto")
                case 25 | 465 | 110 | 143:
                    print("\n recon.py ---> Detectando Serviço de E-mail")
                    
                case _0 :
                    print("\n recon.py ---> Serviço Não Catalogado")
                                    
        while True:
            if self.args.target != None and self.args.port != None:
               
                try:
                    if self.args.port == None:
                        break
                       
                    elif self.args.port == 80:
                        print("\n recon.py ---> Porta HTTP Ativa",  self.args.target)
                    elif self.args.port == 443:
                        print("\n recon.py ---> Porta HTTPS ABERTA no alvo:", self.args.target)
                    elif self.args.port  == 9443 or self.args.port == 8443:
                        print("\n recon.py ---> Porta HTTPS alternativa ABERTA no alvo:", self.args.target)    
                    elif self.args.port == 8080 or self.args.port == 8090 or self.args.port == 8888:
                        print("\n recon.py ---> Porta HTTP alternativa ABERTA no alvo:", self.args.target)
                    elif self.args.port > 19 and self.args.port < 22:
                        print("\n recon.py ---> Porta FTP ABERTA no alvo:", self.args.target)   
                    elif self.args.port  == 22:
                        print("\n recon.py ---> Porta SSH ABERTA no alvo:", self.args.target)       
                    elif self.args.port  == 23:
                        print("\n recon.py ---> Porta Telnet ABERTA no alvo:", self.args.target)       
                    elif self.args.port  == 25:
                        print("\n recon.py ---> Porta SMTP ABERTA no alvo:", self.args.target)
                    elif self.args.port  == 53:
                        print("\n recon.py ---> Porta DNS ABERTA no alvo:", self.args.target)
                    elif self.args.port  == 110:
                        print("\n recon.py ---> Porta POP3 ABERTA no alvo:", self.args.target)
                    elif self.args.port  == 143:
                        print("\n recon.py ---> Porta IMAP ABERTA no alvo:", self.args.target)
                    elif self.args.port  == 465:
                        print("\n recon.py ---> Porta SMTPS ABERTA no alvo:", self.args.target)
                    elif self.args.port  > 988 and self.args.port < 991:
                        print("\n recon.py ---> Porta FTPS ABERTA no alvo:", self.args.target)    
                    elif self.args.port  == 3389:
                        print("\n recon.py ---> Porta RDP ABERTA no alvo:", self.args.target)
                    elif self.args.port  > 49151 and self.args.port < 65536:
                        print("\n recon.py ---> Porta Dinâmica / Efêmera ABERTA no alvo:", self.args.target)     
                    else:
                        print("\n recon.py ---> Porta não identificada ou FECHADA no alvo", self.args.target)
                    break
                except KeyboardInterrupt:
                                print ('\n Interrompido pelo Usuário (CTRL+C)')
                                sys.exit()
                except Exception as e:
                            print(f'\n Finalizado pelo seguinte ERRO: {e}  \n ou Interrompido pelo Usuário (CTRL+D)')
                            sys.exit()
                            break
            else:
                    break
        
                        
    def info(self):
        while True:
            try:
                if self.args.port == None and self.args.target == None:
                    print("\n VALORES NÃO INFORMADOS, TENTE NOVAMENTE. \n")
                    print("Faça: 'recon.py -h' Para obter ajuda. ")
                    print("Ou:   'recon.py -t ALVO.COM -p 443' indicando um ALVO e uma PORTA para escanear.")  
                    self.args.target = (input("\n Se preferir, Digite o ALVO aqui:  "))
                    self.args.port = (int(input("\n E agora, Digite a PORTA aqui:  ")))
                    scanner = Recon(args)
                    scanner.run()
                    print(" \n O programa rodou perfeitamente \n")
                elif self.args.target == None:                    
                     print("\n Valores Selecionados para teste: \n Alvo: NÃO INFORMADO","\n Porta: ", self.args.port)
                     print(" \n TENTE NOVAMENTE \n")
                     print("Faça: 'recon.py -h' Para obter ajuda.")
                     print("Ou:   'recon.py -t alvo.com", "-p", self.args.port,"', por exemplo, indicando um ALVO e uma porta para escanear.")
                     self.args.target = (input("\n Se preferir, Digite o ALVO aqui: "))
                     scanner = Recon(args)
                     scanner.run()
                     print(" \n O programa rodou perfeitamente \n")
                     #scanner.info()
                     
                
                elif self.args.port == None:                    
                     print("\n Valores Selecionados para teste: \n Alvo:", self.args.target, "\n Porta: NÃO INFORMADO")
                     print(" \n TENTE NOVAMENTE \n")
                     print("Faça: 'recon.py -h' Para obter ajuda.")
                     print("Ou:   'recon.py -t", self.args.target,"-p 443', por exemplo, indicando um alvo  e uma porta para escanear.")          
                     self.args.port = (int(input("\n Se preferir, Digite a PORTA aqui: ")))
                     scanner = Recon(args)
                     scanner.run()
                     print(" \n O programa rodou perfeitamente \n")
                     #scanner.info()
                     
                else:
                    print("\n Valores Selecionados para o Teste: \n Alvo: ",self.args.target, "\n Porta: ", self.args.port)
                    print(" \n O programa rodou perfeitamente \n")
                    
            except KeyboardInterrupt:
                print ('\n Interrompido pelo Usuário (CTRL+C)')
                sys.exit()
            except Exception as e:
                print(f'\n Finalizado pelo seguinte ERRO: {e} \n ou Interrompido pelo Usuário (CTRL+D)')
                sys.exit()
            break
                    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Scanner ***recon.py*** por Daniel Amorim",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=('''Exemplo: \r
                            recon.py -t Alvo.com -p 80 \r
                            recon.py -t 192.168.1.1 -p 80 \r '''))
    parser.add_argument('-p', '--port',type=int, help='Porta Númerica')
    parser.add_argument('-t', '--target', type=str, help='Alvo, Endereço IP ou FQDN') #default='127.0.0.1')
    args = parser.parse_args()    
        
    scanner = Recon(args)
    scanner.run()
    scanner.info()