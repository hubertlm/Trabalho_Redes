# REDES I - JOGO DA VELHA MULTIPLAYER UTILIZANDO SOCKETS

Este projeto implementa um jogo da velha multiplayer que permite que duas pessoas joguem em máquinas diferentes através de uma conexão de rede utilizando sockets TCP/IP.

## Como Rodar o Jogo

Para jogar, você precisará de uma máquina para rodar o servidor e duas máquinas para os clientes.

### 1. Executando o Servidor

Na máquina que atuará como servidor:

1.  Abra um terminal ou prompt de comando.
2.  Navegue até o diretório onde o arquivo `servidor.py` está localizado.
3.  Execute o servidor com o comando:
    ```bash
    python servidor.py
    ```
4.  O servidor iniciará e aguardará a conexão de dois clientes.

### 2. Executando os Clientes

Em cada uma das duas máquinas dos jogadores (ou em dois terminais diferentes na mesma máquina para teste):

1.  Abra um terminal ou prompt de comando.
2.  Navegue até o diretório onde o arquivo `cliente.py` está localizado.
3.  Execute o cliente com o comando, substituindo `<ip_do_servidor>` pelo endereço IP real do servidor e `<porta_do_servidor>` pela porta que o servidor está usando:
    ```bash
    python cliente.py <ip_do_servidor> 
    ```
    **Exemplo:**
    ```bash
    python cliente.py 192.168.1.10 
    ```

### 3. Iniciando o Jogo

* O primeiro cliente a se conectar receberá uma mensagem para aguardar o segundo jogador.
* Quando o segundo cliente se conectar, o jogo iniciará automaticamente. O servidor informará a cada jogador qual símbolo ele usará ('X' ou 'O') e de quem é a vez de jogar.
