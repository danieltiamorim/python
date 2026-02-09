import sys

class TextLoader:
    def __init__(self, filename):
        self.filename = filename

    def load_text(self):
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"Erro: O arquivo '{self.filename}' não foi encontrado.")
            sys.exit(1) 

class WordlistGenerator:
    def __init__(self, texto):
        self.texto = texto
        self.wordlist = []

    def generate(self):
        minusculo = self.texto.lower()

        pontuacao = ".,;!?\"'()[]{}"
        for char in pontuacao:
            minusculo = minusculo.replace(char, "")

        raw_words = minusculo.split()

        palavras_unicas = []

        for word in raw_words:
            if len(word) < 3:
                continue
            
            if word not in palavras_unicas:
                palavras_unicas.append(word)

        self.wordlist = palavras_unicas
        print(f"[+] Wordlist gerada com {len(self.wordlist)} palavras únicas.")

    def save(self,output_filename):
        try:
           with open(output_filename, 'w', encoding='utf-8') as f:
                for word in self.wordlist:
                    f.write(word + '\n')
           print(f"[+] Sucesso! Arquivo salvo em: {output_filename}")
        except Exception as e:
            print(f"Erro ao salvar o arquivo: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso correto: python3 wordlist_generator.py <entrada.txt> <saida.txt>")
        print("Exemplo: python3 wordlist_generator.py texto.txt wordlist.txt")
        print("\n Como diria Raul Seixas:'Tente outra vez'")
        sys.exit(1)

    input_filename = sys.argv[1]  
    output_filename = sys.argv[2]

    print("--- Gerador de Wordlist Iniciado ---")

    loader = TextLoader(input_filename)
    content = loader.load_text()

    generator = WordlistGenerator(content)
    generator.generate()
    generator.save(output_filename)