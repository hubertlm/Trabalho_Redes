import socket
import sys

def exibir_tabuleiro_e_mensagem(board_str, mensagem_servidor):
    matriz_jogo = list(board_str) # Converte a string para lista de caracteres
    
    for i in range(len(matriz_jogo)):
        if matriz_jogo[i] == '*':
            matriz_jogo[i] = ' '

    print("\n\n")
    print("\t╔════════════════════════════════════════════════════════╗")
    print("\t║                      Jogo da Velha                     ║")
    print("\t║                                                        ║")
    print("\t║                                                        ║")
    print("\t║                      ╔═══╦═══╦═══╗                     ║")
    print(f"\t║                      ║ {matriz_jogo[0]} ║ {matriz_jogo[1]} ║ {matriz_jogo[2]} ║                     ║")
    print("\t║                      ╠═══╬═══╬═══╣                     ║")
    print(f"\t║                      ║ {matriz_jogo[3]} ║ {matriz_jogo[4]} ║ {matriz_jogo[5]} ║                     ║")
    print("\t║                      ╠═══╬═══╬═══╣                     ║")
    print(f"\t║                      ║ {matriz_jogo[6]} ║ {matriz_jogo[7]} ║ {matriz_jogo[8]} ║                     ║")
    print("\t║                      ╚═══╩═══╩═══╝                     ║")
    print("\t║                                                        ║")
    print("\t╚════════════════════════════════════════════════════════╝")
    print(f"\t Servidor: {mensagem_servidor}")

def parse_pacote_servidor(pacote_str):
    """Interpreta o pacote recebido do servidor."""
    try:
        partes = pacote_str.split('|', 2)
        if len(partes) == 3:
            status_code = partes[0]
            board_str = partes[1]
            mensagem_texto = partes[2]
            return status_code, board_str, mensagem_texto
        else:
            print(f"Erro: Pacote malformado recebido: {pacote_str}")
            return None, None, None
    except Exception as e:
        print(f"Erro ao parsear pacote: {e} - Pacote: {pacote_str}")
        return None, None, None

def main():
    if len(sys.argv) < 2:
        print("Uso: python cliente.py <ip_servidor>")
        return

    HOST_SERVIDOR = sys.argv[1]
    PORTA_SERVIDOR = 5000
    
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"Tentando conectar a {HOST_SERVIDOR}:{PORTA_SERVIDOR}...")
        cliente_socket.connect((HOST_SERVIDOR, PORTA_SERVIDOR))
        print("Conectado ao servidor!")
    except socket.error as e:
        print(f"Erro ao conectar: {e}")
        return

    try:
        jogo_ativo = True
        while jogo_ativo:
            dados_recebidos = cliente_socket.recv(1024)
            if not dados_recebidos:
                print("Servidor desconectou ou fechou a conexão.")
                jogo_ativo = False
                break
            
            pacote_str = dados_recebidos.decode('utf-8')
            status_code, board_str, mensagem_texto = parse_pacote_servidor(pacote_str)

            if status_code is None: # Erro no parse
                print("Encerrando devido a erro no pacote.")
                jogo_ativo = False
                break

            system_clear = "\033[H\033[J" # Código ANSI para limpar console 
            print(system_clear) # Limpa a tela 
            exibir_tabuleiro_e_mensagem(board_str, mensagem_texto)

            # Códigos de status que indicam fim de jogo
            if status_code in ["2", "3", "4"]:
                print("\nJogo encerrado.")
                jogo_ativo = False
                break
            
            # Código de status que solicita uma jogada
            if status_code == "5" or status_code == "1": # Vez do jogador
                while True:
                    jogada_input = input("\t Coordenada (1-9): ").strip()
                    if jogada_input.isdigit() and 1 <= int(jogada_input) <= 9 and len(jogada_input)==1:
                        cliente_socket.sendall(jogada_input.encode('utf-8'))
                        break 
                    else:
                        print("\t Entrada inválida. Digite um número de 1 a 9.")

    except ConnectionResetError:
        print("Conexão resetada pelo servidor.")
    except BrokenPipeError:
        print("Conexão interrompida com o servidor (Broken Pipe).")
    except KeyboardInterrupt:
        print("\nJogo encerrado pelo usuário.")
    except Exception as e:
        print(f"Erro inesperado: {e}")
    finally:
        print("Fechando socket do cliente.")
        cliente_socket.close()

if __name__ == "__main__":
    main()