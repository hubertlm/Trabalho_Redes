import socket
import threading 

HOST = '0.0.0.0'  # Escuta em todas as interfaces disponíveis
PORTA_PADRAO = 5000

# Primeiro jogador a se conectar vai ser o X e o segundo O
VALOR_X = -1
VALOR_O = 1
VAZIO = 0

def inicializar_tabuleiro():
    return [[VAZIO for _ in range(3)] for _ in range(3)]

def tabuleiro_para_string(tabuleiro_matriz):
    s = ""
    for i in range(3):
        for j in range(3):
            if tabuleiro_matriz[i][j] == VALOR_X:
                s += "X"
            elif tabuleiro_matriz[i][j] == VALOR_O:
                s += "O"
            else:
                s += "*" 
    return s

def coordenada_para_indices(coord_str):
    if not coord_str.isdigit() or not (1 <= int(coord_str) <= 9):
        return None, None, None
    
    coord_num = int(coord_str) - 1 # Convertendo para base 0 (0-8)
    linha = coord_num // 3
    coluna = coord_num % 3
    return linha, coluna, coord_num

def valida_coordenada(tabuleiro_matriz, linha, coluna, coord_digitadas_linear):
    if not (0 <= linha < 3 and 0 <= coluna < 3):
        return False
    if tabuleiro_matriz[linha][coluna] != VAZIO:
        return False
    return True
    
def verifica_fim_matriz(tabuleiro_matriz, num_jogadas):

    linhas = [sum(tabuleiro_matriz[r][c] for c in range(3)) for r in range(3)]
    colunas = [sum(tabuleiro_matriz[r][c] for r in range(3)) for c in range(3)]
    diag1 = sum(tabuleiro_matriz[i][i] for i in range(3))
    diag2 = sum(tabuleiro_matriz[i][2 - i] for i in range(3))

    somas = linhas + colunas + [diag1, diag2]

    for soma in somas:
        if soma == 3 * VALOR_X: return VALOR_X # X ganhou
        if soma == 3 * VALOR_O: return VALOR_O # O ganhou
    
    if num_jogadas == 9:
        return 9 # Empate 
    
    return 0

def montar_pacote_servidor(status_code, tabuleiro_matriz, mensagem_texto):
    board_str = tabuleiro_para_string(tabuleiro_matriz)
    return f"{status_code}|{board_str}|{mensagem_texto}"

def lidar_com_jogo(cliente1_conn, cliente1_addr, cliente2_conn, cliente2_addr):
    print(f"Iniciando jogo entre {cliente1_addr} (X) e {cliente2_addr} (O)")

    tabuleiro_atual = inicializar_tabuleiro()
    coord_digitadas_linear = [] 
    num_jogadas = 0
    
    jogadores = {
        VALOR_X: (cliente1_conn, cliente1_addr, "X"),
        VALOR_O: (cliente2_conn, cliente2_addr, "O")
    }
    jogador_corrente_valor = VALOR_X # X começa

    # Mensagens iniciais 
    msg_aguarde_inicial = "Aguarde sua vez para jogar!"
    pacote_aguarde_c1 = montar_pacote_servidor("6", tabuleiro_atual, f"{msg_aguarde_inicial} Você é X.")
    cliente1_conn.sendall(pacote_aguarde_c1.encode('utf-8'))
    
    pacote_aguarde_c2 = montar_pacote_servidor("6", tabuleiro_atual, f"{msg_aguarde_inicial} Você é O.")
    cliente2_conn.sendall(pacote_aguarde_c2.encode('utf-8'))

    # Mensagem para o primeiro jogador iniciar 
    pacote_iniciar_c1 = montar_pacote_servidor("5", tabuleiro_atual, "Sua vez (X). Faça uma jogada (1-9):")
    cliente1_conn.sendall(pacote_iniciar_c1.encode('utf-8'))

    try:
        while True:
            conn_ativo, addr_ativo, simb_ativo = jogadores[jogador_corrente_valor]
            conn_espera, _, simb_espera = jogadores[jogador_corrente_valor * -1] # Pega o outro jogador

            print(f"Aguardando jogada do Jogador {simb_ativo} ({addr_ativo})")
            
            jogada_valida_recebida = False
            while not jogada_valida_recebida:
                try:
                    dados_recebidos = conn_ativo.recv(1024)
                    if not dados_recebidos:
                        print(f"Jogador {simb_ativo} ({addr_ativo}) desconectou.")
                        # Informar o outro jogador
                        pacote_desconexao = montar_pacote_servidor("3", tabuleiro_atual, "Oponente desconectou. Você ganhou por W.O.")
                        conn_espera.sendall(pacote_desconexao.encode('utf-8'))
                        return # Encerra o handler do jogo
                    
                    jogada_str = dados_recebidos.decode('utf-8').strip()
                    print(f"Jogador {simb_ativo} jogou: {jogada_str}")

                    linha, coluna, coord_linear_idx = coordenada_para_indices(jogada_str)

                    if linha is None or not valida_coordenada(tabuleiro_atual, linha, coluna, coord_digitadas_linear):
                        print(f"Jogada inválida de {simb_ativo}: {jogada_str}")
                        msg_invalida = "Coordenada já ocupada. Tente novamente (1-9):"
                        pacote_invalido = montar_pacote_servidor("1", tabuleiro_atual, msg_invalida)
                        conn_ativo.sendall(pacote_invalido.encode('utf-8'))
                        continue 
                    
                    # Jogada válida
                    tabuleiro_atual[linha][coluna] = jogador_corrente_valor
                    coord_digitadas_linear.append(coord_linear_idx) # Adiciona à lista de jogadas (0-8)
                    num_jogadas += 1
                    jogada_valida_recebida = True

                except ConnectionResetError:
                    print(f"Jogador {simb_ativo} ({addr_ativo}) resetou a conexão.")
                    pacote_desconexao = montar_pacote_servidor("3", tabuleiro_atual, "Oponente desconectou. Você ganhou por W.O.")
                    conn_espera.sendall(pacote_desconexao.encode('utf-8'))
                    return
                except Exception as e:
                    print(f"Erro ao receber de {simb_ativo}: {e}")
                    return

            # Verificar fim do jogo
            status_fim = verifica_fim_matriz(tabuleiro_atual, num_jogadas)
            
            if status_fim != 0: # Jogo terminou
                msg_vencedor = ""
                msg_perdedor = ""
                msg_empate = "FIM DE JOGO, DEU VELHA!!!"

                if status_fim == VALOR_X: # X ganhou
                    print("Jogador X venceu!")
                    pacote_vencedor_x = montar_pacote_servidor("2", tabuleiro_atual, "FIM DE JOGO, VOCÊ GANHOU!!!")
                    cliente1_conn.sendall(pacote_vencedor_x.encode('utf-8'))
                    pacote_perdedor_o = montar_pacote_servidor("3", tabuleiro_atual, "FIM DE JOGO, VOCÊ PERDEU!!!")
                    cliente2_conn.sendall(pacote_perdedor_o.encode('utf-8'))
                elif status_fim == VALOR_O: # O ganhou
                    print("Jogador O venceu!")
                    pacote_vencedor_o = montar_pacote_servidor("2", tabuleiro_atual, "FIM DE JOGO, VOCÊ GANHOU!!!")
                    cliente2_conn.sendall(pacote_vencedor_o.encode('utf-8'))
                    pacote_perdedor_x = montar_pacote_servidor("3", tabuleiro_atual, "FIM DE JOGO, VOCÊ PERDEU!!!")
                    cliente1_conn.sendall(pacote_perdedor_x.encode('utf-8'))
                elif status_fim == 9: # Empate
                    print("Empate!")
                    pacote_empate_ambos = montar_pacote_servidor("4", tabuleiro_atual, msg_empate)
                    cliente1_conn.sendall(pacote_empate_ambos.encode('utf-8'))
                    cliente2_conn.sendall(pacote_empate_ambos.encode('utf-8'))
                break

            else: # Jogo continua
                # Enviar "Aguarde sua vez" para o jogador que acabou de jogar
                msg_aguarde_ativo = f"Jogada em {jogada_str} registrada. Aguarde a vez de {simb_espera}."
                pacote_aguarde_ativo = montar_pacote_servidor("0", tabuleiro_atual, msg_aguarde_ativo)
                conn_ativo.sendall(pacote_aguarde_ativo.encode('utf-8'))

                # Enviar "Sua vez" para o próximo jogador
                msg_vez_espera = f"Vez de {simb_espera}. Jogador {simb_ativo} jogou em {jogada_str}. Faça uma jogada (1-9):"
                pacote_vez_espera = montar_pacote_servidor("5", tabuleiro_atual, msg_vez_espera)
                conn_espera.sendall(pacote_vez_espera.encode('utf-8'))
                
                # Alternar jogador
                jogador_corrente_valor *= -1 
                
    except Exception as e:
        print(f"Erro durante o jogo: {e}")
    finally:
        print(f"Encerrando jogo entre {cliente1_addr} e {cliente2_addr}")
        cliente1_conn.close()
        cliente2_conn.close()


def main():
    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Permite reusar o endereço
    try:
        servidor_socket.bind((HOST, PORTA_PADRAO))
    except socket.error as e:
        print(f"Erro no bind: {e}")
        return
    
    servidor_socket.listen(2) # Escuta até 2 conexões na fila
    print(f"Servidor do Jogo da Velha escutando em {HOST}:{PORTA_PADRAO}")

    while True: # Loop para aceitar novas duplas de jogadores
        clientes_conectados = []
        enderecos_clientes = []
        print("\nAguardando jogadores...")
        try:
            while len(clientes_conectados) < 2:
                conn, addr = servidor_socket.accept()
                print(f"Cliente {len(clientes_conectados) + 1} conectado: {addr}")
                clientes_conectados.append(conn)
                enderecos_clientes.append(addr)
                conn.sendall(montar_pacote_servidor("6", inicializar_tabuleiro(), f"Conectado! Aguardando outro jogador... Você é o jogador {len(clientes_conectados)}.").encode('utf-8'))

            # Inicia uma nova thread para lidar com o jogo desta dupla
            thread_jogo = threading.Thread(target=lidar_com_jogo, args=(
                clientes_conectados[0], enderecos_clientes[0],
                clientes_conectados[1], enderecos_clientes[1]
            ))
            thread_jogo.daemon = True # Permite que o programa principal saia mesmo se threads estiverem rodando
            thread_jogo.start()
        
        except KeyboardInterrupt:
            print("\nServidor encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"Erro no loop principal do servidor: {e}")
            for conn in clientes_conectados:
                conn.close()
            break 

    servidor_socket.close()

if __name__ == "__main__":
    main()