"""
Classe principal que lê o arquivo e obtém os dados.
"""

from datetime import datetime
import io

class FK7:
    """
    Classe para manipulação de arquivos FK7.
    """
    def __init__(self, arquivo: str):
        """
        Inicializa a instância da classe com o caminho do arquivo FK7.
        :param arquivo: Caminho ou bytes do arquivo FK7.
        """
        
        # Verifica se parâmetro passado é caminho ou bytes
        if isinstance(arquivo, str):
            # É um caminho para arquivo
            self.caminho_arquivo = arquivo
            self.bytes = None
        elif isinstance(arquivo, bytes):
            # É um conteúdo binário
            self.caminho_arquivo = None
            self.bytes = arquivo
        else:
            raise TypeError("A variável 'arquivo' deve ser uma string (caminho) ou bytes.")
        
        # Atributos

        self.dado_bruto = None # Dados brutos
        self.hex_blocos = [] # Lista contendo os blocos com dados hexadecimais
        self.qtd_blocos = None # Quantidade de blocos encontrados no arquivo
        self.bloco_presente = {'20':False, '21':False, '22':False, '51':False, '23':False, '24':False, '41':False, '44':False, '42':False, '43':False, '45':False, '46':False, '25':False, '26':False, '27':False, '52':False, '28':False, '80':False, '14':False} # Registra a presença dos tipos diferentes de blocos de leitura
        self.serial_medidor = None # Número do medidor
        self.data_hora_atual = None # Data e hora atual no medidor
        
        # Lê o arquivo assim que a instância da classe é criada
        self.__lerArquivo()

    def __lerArquivo(self):
        """
        Função interna.
        Lê o conteúdo do arquivo FK7 e obtém os atributos.
        """
        try:
            
            if self.caminho_arquivo:
                with open(self.caminho_arquivo, 'rb') as f:
                    dados = f.read()
            elif self.bytes:
                f = io.BytesIO(self.bytes)
                dados = f.read()

            # Dados brutos:
            self.dado_bruto = dados
            
            # Divide os dados em blocos de 256 octetos
            tamanho_bloco = 256
            self.hex_blocos = [ [f"{byte:02X}" for byte in dados[i:i + tamanho_bloco]] for i in range(0, len(dados), tamanho_bloco)]
            self.qtd_blocos = len(self.hex_blocos)

            # Identifica os blocos presentes pelo primeiro octeto
            for bloco in self.hex_blocos:
                if bloco[0] in ('20', '21', '22', '51', '23', '24', '41', '44', '42', '43', '45', '46', '25', '26', '27', '52', '28', '80', '14'):
                    self.bloco_presente[bloco[0]] = True

            # Busca o número do medidor:
            self.serial_medidor = self.__obtemSerialMedidor()
            # Encontra data e hora atual no arquivo:
            self.data_hora_atual = self.__obtemDataHora()
            # Gera o nome padrão do arquivo segundo a norma
            self.nome_arquivo = self.__obtemNomeArquivo()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho_arquivo}")
        except Exception as e:
            raise IOError(f"Erro ao ler o arquivo: {e}")

    def __obtemSerialMedidor(self):
        """
        Função interna.
        Tenta encontrar o número do medidor através dos blocos lidos.
        """
        serial_encontrado = []

        # Octetos que contém o número do medidor de acordo com a norma NBR 14522
        # Variáveis criadas para facilitar o entendimento
        octeto_inicial = 2
        octeto_final = 5
        
        # Obtém o número do medidor de cada bloco de leitura
        for bloco in self.hex_blocos:
            if bloco[0] in ('20', '21', '22', '51', '23', '24', '41', '44', '42', '43', '45', '46', '26', '27', '52', '28', '80', '14'):
                serial_encontrado.append(int(''.join(bloco[octeto_inicial-1:octeto_final])))
        
        # Verifica se encontrou número de medidor nos blocos e compara se são todos iguais.
        # Se houver diferença entre números de medidores, pode haver algum problema com o arquivo fk7.
        if len(serial_encontrado) > 0:
            if all(item == serial_encontrado[0] for item in serial_encontrado):
                return serial_encontrado[0]
            else:
                raise Exception("Foram encontrados números de medidores distintos no arquivo. Verifique o arquivo.")
        else:
            raise Exception("Não foi encontrado nenhum número de medidor no arquivo.")

    def __obtemDataHora(self):
        """
        Função interna.
        Obtém dados de data e hora.
        """
        data_hora_encontrado = []

        # Octetos que contém a data e a hora de acordo com a norma NBR 14522
        # Variáveis criadas para facilitar o entendimento
        octeto_inicial = 6
        octeto_final = 11

        # Formato da data no arquivo fk7
        formato = "%H%M%S%d%m%y"
        
        # Obtém os dados de data e hora dos blocos de leitura 20, 21, 22 ou 51
        for bloco in self.hex_blocos:
            if bloco[0] in ('20', '21', '22', '51'):
                data_hora_bruto = ''.join(bloco[octeto_inicial-1:octeto_final])
                data_hora_convertido = datetime.strptime(data_hora_bruto, formato)
                data_hora_encontrado.append(data_hora_convertido)
        
        # Verifica se encontrou a data e hora nos blocos e compara se são todos iguais.
        # Se houver diferença entre data e hora dos blocos, pode haver algum problema com o arquivo fk7.
        if len(data_hora_encontrado) > 0:
            if all(item == data_hora_encontrado[0] for item in data_hora_encontrado):
                return data_hora_encontrado[0]
            else:
                #raise Exception("Foram encontrados registros de data e hora distintos no arquivo. Verifique o arquivo.")
                print("Foram encontrados registros de data e hora distintos no arquivo. Verifique o arquivo.")
                return data_hora_encontrado[0]
        else:
            raise Exception("Não foi encontrado nenhum registro de data e hora no arquivo.")

    def __obtemNomeArquivo(self):
        # Extrair os cinco últimos dígitos do número de série do medidor
        nnnnn = str(self.serial_medidor)[-5:]
        
        # Extrair os componentes de data e hora
        segundo = self.data_hora_atual.second
        minuto = self.data_hora_atual.minute
        hora = self.data_hora_atual.hour
        dia = self.data_hora_atual.day
        mes = self.data_hora_atual.month
        
        # Cálculo do total de segundos
        total_segundos = segundo + (minuto * 60) + (hora * 3600) + (dia * 24 * 3600) + (mes * 31 * 24 * 3600)
        
        # Função para converter para base 20
        def para_base_20(numero):
            caracteres_base_20 = "ABCDEFGHIJKLMNOPQRST"
            resultado = ""
            while numero > 0:
                resultado = caracteres_base_20[numero % 20] + resultado
                numero //= 20
            return resultado
        
        # Converter o total de segundos para base 20
        base_20 = para_base_20(total_segundos)
        
        # Obter os 5 primeiros caracteres ou completar com zeros
        base_20 = base_20[-5:].rjust(5, 'A')
        
        # Formar o nome do arquivo
        nome_arquivo = f"{nnnnn}${base_20[0:2]}.{base_20[2:5]}"
        return nome_arquivo
