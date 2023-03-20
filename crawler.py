import re
import threading
import multiprocessing


import requests
from bs4 import BeautifulSoup

DOMINIO = 'https://django-anuncios.solyd.com.br'
URL_AUTOMOVEIS = 'https://django-anuncios.solyd.com.br/automoveis/'

LINKS = []
TELEFONES = []


def descobrir_quantidade_processadores():
    try:
        num_processadores = multiprocessing.cpu_count()
        return num_processadores
    except Exception as error:
        print('Não foi possível descobrir a quantidade de processadores!')
        print('Erro: {}'.format(error))


def buscar_anuncios(url):
    try:
        resposta = requests.get(url)

        if (resposta.status_code == 200):
            return resposta.text
        else:
            print('A requisição deu errado!')
    except Exception as error:
        print('A requisição realizada no endpoint {} não deu certo!'.format(
            URL_AUTOMOVEIS))
        print('Erro: {}'.format(error))


def parsing_html(resposta):
    try:
        soup = BeautifulSoup(resposta, 'html.parser')
        return soup
    except Exception as error:
        print('O parsing do HTML não deu certo!')
        print('Erro: {}'.format(error))


teste = buscar_anuncios(URL_AUTOMOVEIS)
parsing_html(teste)


def encontrar_links(parsingHtml):
    try:
        listaLinks = []
        links = parsingHtml.find_all('a', class_='card')

        for link in links:
            listaLinks.append(DOMINIO + link.get('href'))

        return listaLinks
    except Exception as error:
        print('Não foi possível encontrar o link!')
        print('Erro: {}'.format(error))


def encontrar_telefone(anuncioComParsing):
    try:
        descricao_anuncio = anuncioComParsing.find_all(
            'div', class_='sixteen wide column')[2].p.get_text().strip()

        regex = re.findall(
            r'\(?0?([1-9]{2})[ \-\.\)]{0,2}(9[ \-\.\)]?\d{4})[ \-\.\)]?(\d{4})', descricao_anuncio)

        if regex:
            return regex
        else:
            return None

    except Exception as error:
        print('Não foi possível encontrar o telefone!')
        print('Erro: {}'.format(error))


# Buscando os telefones que podem ser encontrados dentro da descrição de cada anúncio específico
def buscar_telefones():
    try:
        while (len(LINKS) > 0):
            anuncio = buscar_anuncios(LINKS.pop(0))
            if anuncio:
                anuncioParseado = parsing_html(anuncio)
                if anuncioParseado:
                    telefones = encontrar_telefone(anuncioParseado)
                    if telefones:
                        for telefone in telefones:
                            TELEFONES.append(telefone)
                            salvar_telefones(telefone)
    except Exception as error:
        print('Não foi possível buscar os telefones!')
        print('Erro: {}'.format(error))


def salvar_telefones(telefone):
    try:
        string_telefone = '{}{}{}'.format(
            telefone[0], telefone[1], telefone[2])

        with open('telefones.csv', 'a') as arquivo_telefones:
            arquivo_telefones.write(string_telefone+'\n')

    except Exception as error:
        print('Não foi possível salvar o telefone!')
        print('Erro: {}'.format(error))


if __name__ == '__main__':
    print('-------------------------------------------------------------------------------------------------------------------------------------')
    quantidade_threads = descobrir_quantidade_processadores()
    print('Este código será melhor executado com {} threads\n'.format(
        quantidade_threads))
    print('Por padrão ele está setado com 4 threads, pois meu computador possui apenas 4 núcleos - 2 físicos e 2 virtuais (hyperthreading)')
    print('-------------------------------------------------------------------------------------------------------------------------------------\n')

    print('LISTA DE TELEFONES DISPONÍVEIS NO ARQUIVO: telefones.csv')

    # Buscando todos os links de anúncios
    respostaRequisicao = buscar_anuncios(URL_AUTOMOVEIS)
    if respostaRequisicao:
        htmlParseado = parsing_html(respostaRequisicao)
        if htmlParseado:
            LINKS = encontrar_links(htmlParseado)

            THREADS = []

            # Criando as threads
            for i in range(quantidade_threads):
                thread = threading.Thread(target=buscar_telefones)
                THREADS.append(thread)

            # Iniciando as threads
            for t in THREADS:
                t.start()

            # Esperando as threads terminarem para poder finalizar o código
            for t in THREADS:
                t.join()

    print('\nFinalizado com sucesso!\n')

'''
MANEIRA ARCAICA DE FAZER THREADS:
---------------------------------
# Criando as threads
thread_1 = threading.Thread(target=buscar_telefones)
thread_2 = threading.Thread(target=buscar_telefones)
thread_3 = threading.Thread(target=buscar_telefones)
thread_4 = threading.Thread(target=buscar_telefones)

# Iniciando as threads
thread_1.start()
thread_2.start()
thread_3.start()
thread_4.start()

# Esperando as threads terminarem para poder finalizar o código
thread_1.join()
thread_2.join()
thread_3.join()
thread_4.join()
'''
