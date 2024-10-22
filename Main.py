import os
import csv
import sqlite3
from pathlib import Path
import shutil
from datetime import datetime


caminho_atual = os.getcwd()
caminhoBackups = os.path.join(caminho_atual, 'backups')
caminhoData = os.path.join(caminho_atual, 'data')
caminhoExports = os.path.join(caminho_atual, 'exports')

os.makedirs(caminhoData, exist_ok=True)
os.makedirs(caminhoBackups, exist_ok=True)
os.makedirs(caminhoExports, exist_ok=True)

conexao = sqlite3.connect('./data/livraria.db')
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS livros (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT NOT NULL,
        autor TEXT NOT NULL,
        ano_publicacao INTEGER NOT NULL,
        preco DOUBLE NOT NULL
    )
''')

livrosImportados = []

def FazerBackup():
    dbAtual = Path(f'{caminhoData}/livraria.db')
    data_hora_atual = datetime.now()
    arquivo_duplicado = Path(caminhoBackups) / f'livrariaBeckup-{data_hora_atual.strftime('%Y%m%d_%H%M%S')}.db'
    shutil.copy(dbAtual, arquivo_duplicado)
    LimparBackupAntigo()

def LimparBackupAntigo():
    backups = sorted(Path(caminhoBackups).glob('livrariaBeckup-*.db'), key=os.path.getmtime)
    while len(backups) > 5:
        os.remove(backups.pop(0))


def ImportarLivros(caminho):
    FazerBackup()
    caminho = caminho.replace('\\', '/')
    with open(caminho, 'r') as arquivo:
        for linha in arquivo:
            dado = linha.strip().split("-") 
            livrosImportados.append((dado[0], dado[1], int(dado[2]), float(dado[3])))
    
    try:
        cursor.executemany('''
            INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)
        ''', (livrosImportados))
        cursor.connection.commit()
        print("Livro adicionado com sucesso!")
    except Exception as e:
        print("Ocorreu um erro ao adicionar o livro:", e)



def ExportarInfo():
    cursor.execute('SELECT * FROM livros')
    livros = cursor.fetchall()
    data_hora_atual = datetime.now()
    with open(Path(caminhoExports) / f'livros_exportados{data_hora_atual.strftime('%Y%m%d_%H%M%S')}.csv', mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['ID', 'Título', 'Autor', 'Ano de Publicação', 'Preço'])
        writer.writerows(livros)

def AdicionarLivro (titulo, autor, ano_publicacao, preco):
    FazerBackup()
    try:
        cursor.execute('''
            INSERT INTO livros (titulo, autor, ano_publicacao, preco) VALUES (?, ?, ?, ?)
        ''', (titulo, autor, ano_publicacao, preco))
        cursor.connection.commit()
        print("Livro adicionado com sucesso!")
    except Exception as e:
        print("Ocorreu um erro ao adicionar o livro:", e)

def ListarLivro():
    cursor.execute('SELECT * FROM livros')
    resultado = cursor.fetchall()
    
    for linha in resultado:
        print(f'ID: {linha[0]}, Titulo: {linha[1]}, Autor: {linha[2]}, Ano Publicação: {linha[3]}, Preço: {linha[4]}')


def AlterarValorLivro(titulo, novoValor):
    FazerBackup()
    try:
        cursor.execute('UPDATE livros SET preco = ? WHERE titulo = ?', (novoValor, titulo))
        cursor.connection.commit()
        print("Livro editado com sucesso!")
    except Exception as e:
        print("Ocorreu um erro ao editar o livro:", e)
    
def DeletarLivro(titulo):
    try:
        cursor.execute('''
            DELETE FROM livros WHERE titulo = ?
        ''', (titulo, ))
        cursor.connection.commit()
        print("Livro deletado com sucesso!")
    except Exception as e:
        print("Ocorreu um erro ao deletar o livro:", e)

def BuscarPorAutor(autor):
    cursor.execute('SELECT * FROM livros WHERE autor=?', (autor, ))
    resultado = cursor.fetchall()

    for linha in resultado:
        print(f'ID: {linha[0]}, Titulo: {linha[1]}, Autor: {linha[2]}, Ano Publicação: {linha[3]}, Preço: {linha[4]}')

cond = True
while(cond == True):
    print("1. Adicionar novo livro")
    print("2. Exibir todos os livros")
    print("3. Atualizar preço de um livro")
    print("4. Remover um livro")
    print("5. Buscar livros por autor")
    print("6. Exportar dados para CSV")
    print("7. Importar dados de CSV")
    print("8. Fazer backup do banco de dados")
    print("9. Sair")
    opcao = int(input('Digite a opção: '))
    
    if (opcao == 1):
        titulo = input('Titulo do livro: ')
        autor = input('Autor do livro: ')
        ano_publicacao = int(input('Ano publicacao do livro: '))
        preco = float(input('Preço do livro: '))

        AdicionarLivro(titulo, autor, ano_publicacao, preco)
    elif (opcao == 2):
        ListarLivro()
    elif (opcao == 3):
        titulo = input('Titulo do livro a ser alterado: ')
        novoValor = float(input('Novo valor do livro: '))
        AlterarValorLivro(titulo, novoValor)
    elif (opcao == 4):
        titulo = input('Titulo do livro a ser deletado: ')
        DeletarLivro(titulo)
    elif (opcao == 5):
        autor = (input("Digite o nome do autor: "))
        BuscarPorAutor(autor)
    elif (opcao == 6):
        ExportarInfo()
        print("Informações exportadas!!!")
    elif (opcao == 7):
        caminho = input("Insira o caminho do CSV para ser Importado: ")
        ImportarLivros(caminho)
    elif (opcao == 8):
        FazerBackup()
    elif (opcao == 9):
        cond=False
    else: 
        cond=True

