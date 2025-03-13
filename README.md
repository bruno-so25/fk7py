# FK7-Python
Conjunto de scripts python para leitura e interpretação de arquivos fk7.

🎯 Objetivo

Este projeto tem como objetivo facilitar a leitura e interpretação de arquivos fk7.
Os scripts deste projeto interpretam o arquivo fk7 de acordo com o que é apresentado na norma ABNT NBR 14522.

🖥️ Exemplo de utilização

Modo básico: Coloque o arquivo FK7Python.py no mesmo diretório do seu código, e importe conforme exemplo a seguir:

```python 

from FK7Python import FK7File

caminho_do_arquivo = 'C:/caminho/do/arquivo'

arquivo = FK7File(caminho_do_arquivo)

# Imprime o número do medidor
print(arquivo.serial_medidor)  # Saída: 00000000

```

✒️ Autores

Bruno Oliveira
