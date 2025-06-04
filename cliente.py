import socket
import os

PORTA_PADRAO = 4343
INICIO_MATRIZ = 1
INICIO_TAM_MSG = 10
INICIO_MSG = 12

def iniciar_socket(ip):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, PORTA_PADRAO))
    print("Conectado! Aguarde resposta do servidor...\n")
    return sock

def verifica_recuso(c):
    return c == 'x'

def analisa_fim_pacote(pacote):
    return pacote[INICIO_MSG:INICIO_MSG+3] == "FIM"

def convert_char(c):
    return int(c)

def char_para_int(pacote):
    return 10 * convert_char(pacote[INICIO_TAM_MSG]) + convert_char(pacote[INICIO_TAM_MSG + 1])

def desencapsular(pacote):
    matriz_jogo = [' ' if c == '*' else c for c in pacote[INICIO_MATRIZ:INICIO_MATRIZ+9]]
    tam = char_para_int(pacote)
    mensagem = pacote[INICIO_MSG:INICIO_MSG+tam]
    return matriz_jogo, mensagem

def imprimir(matriz_jogo, mensagem_servidor):
    print("\n\n\n\tJogo da Velha")
    print("\t╔═══╦═══╦═══╗")
    for i in range(3):
        print(f"\t║ {matriz_jogo[3*i]} ║ {matriz_jogo[3*i+1]} ║ {matriz_jogo[3*i+2]} ║")
        if i < 2:
            print("\t╠═══╬═══╬═══╣")
    print("\t╚═══╩═══╩═══╝")
    print(f"\tServidor: {mensagem_servidor}")
    print("\tCoordenada:", end=' ')

def cliente(ip):
    sock = iniciar_socket(ip)
    fim = False

    for _ in range(2):
        pacote = sock.recv(100).decode()
        matriz_jogo, mensagem = desencapsular(pacote)
        os.system("clear")
        imprimir(matriz_jogo, mensagem)

    while not fim:
        while True:
            jogada = input()
            sock.sendall(jogada.encode())

            pacote = sock.recv(100).decode()
            matriz_jogo, mensagem = desencapsular(pacote)
            os.system("clear")
            imprimir(matriz_jogo, mensagem)

            if analisa_fim_pacote(pacote) or not verifica_recuso(pacote[0]):
                break

        if not analisa_fim_pacote(pacote):
            pacote = sock.recv(100).decode()
            matriz_jogo, mensagem = desencapsular(pacote)
            os.system("clear")
            imprimir(matriz_jogo, mensagem)
            fim = analisa_fim_pacote(pacote)
        else:
            fim = True

    print("\n\n")
    sock.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Informe o IP do servidor!")
    else:
        cliente(sys.argv[1])
