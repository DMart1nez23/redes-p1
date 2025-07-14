# ==========================================
# Bibliotecas
# ==========================================
import socket
import select

# ==========================================
# Constantes
# ==========================================
HOST = ''  # Escuta em todas as interfaces
PORT = 6667
MAX_BUFFER_SIZE = 1024

# ==========================================
# Variáveis Globais
# ==========================================
moonwalkConnections = []
badNicknames = {}
thrillerChannels = {}

# ==========================================
# Funções auxiliares
# ==========================================
def validar_nome(nome):
    return nome and nome.isalnum()

def enviar(conexao, mensagem):
    conexao.send((mensagem + '\r\n').encode())

def broadcast_para_canal(nome_canal, mensagem, ignorar=None):
    for user in thrillerChannels.get(nome_canal.lower(), set()):
        if user != ignorar:
            enviar(user, mensagem)

# ==========================================
# Classe da Conexão
# ==========================================
class BillieJean:
    def __init__(self, sock, addr):
        self.socket = sock
        self.addr = addr
        self.thrillerBuffer = ""
        self.smoothCriminalNick = None
        self.dirtyDianaChannels = set()

    def processar_dados(self, dados_recebidos):
        self.thrillerBuffer += dados_recebidos

        while '\r\n' in self.thrillerBuffer:
            linha, self.thrillerBuffer = self.thrillerBuffer.split('\r\n', 1)
            self._processar_mensagem(linha.strip())

    def _processar_mensagem(self, linha):
        if not linha:
            return

        partes = linha.split()
        comando = partes[0].upper()

        if comando == 'PING':
            enviar(self.socket, 'PONG')

        elif comando == 'NICK':
            if len(partes) < 2:
                enviar(self.socket, '432 :No nickname given')
                return

            novo_nick = partes[1]
            if not validar_nome(novo_nick):
                enviar(self.socket, f'432 {novo_nick} :Erroneous nickname')
                return

            nick_lower = novo_nick.lower()
            if nick_lower in badNicknames and badNicknames[nick_lower] != self:
                enviar(self.socket, f'433 {novo_nick} :Nickname is already in use')
                return

            if self.smoothCriminalNick:
                del badNicknames[self.smoothCriminalNick.lower()]
            self.smoothCriminalNick = novo_nick
            badNicknames[nick_lower] = self
            enviar(self.socket, f'001 {novo_nick} :Welcome to the MJ Chat Server')
            enviar(self.socket, f'422 {novo_nick} :MOTD File is missing')

        elif comando == 'PRIVMSG':
            if len(partes) < 3:
                return
            destino = partes[1]
            mensagem = linha.split(":", 1)[1] if ":" in linha else ""

            if destino.startswith("#"):
                canal = destino.lower()
                if canal in thrillerChannels:
                    broadcast_para_canal(canal, f":{self.smoothCriminalNick} PRIVMSG {destino} :{mensagem}", ignorar=self)
            else:
                receptor = badNicknames.get(destino.lower())
                if receptor:
                    enviar(receptor.socket, f":{self.smoothCriminalNick} PRIVMSG {destino} :{mensagem}")

        elif comando == 'JOIN':
            if len(partes) < 2:
                return
            nome_canal = partes[1].lower()
            if nome_canal not in thrillerChannels:
                thrillerChannels[nome_canal] = set()
            thrillerChannels[nome_canal].add(self)
            self.dirtyDianaChannels.add(nome_canal)
            enviar(self.socket, f":{self.smoothCriminalNick} JOIN {nome_canal}")
            # 353 e 366
            membros = [conn.smoothCriminalNick for conn in thrillerChannels[nome_canal]]
            enviar(self.socket, f"353 = {nome_canal} :{' '.join(membros)}")
            enviar(self.socket, f"366 {nome_canal} :End of /NAMES list")

        elif comando == 'PART':
            if len(partes) < 2:
                return
            nome_canal = partes[1].lower()
            if nome_canal in thrillerChannels and self in thrillerChannels[nome_canal]:
                thrillerChannels[nome_canal].remove(self)
                self.dirtyDianaChannels.discard(nome_canal)
                enviar(self.socket, f":{self.smoothCriminalNick} PART {nome_canal}")

    def sair(self):
        if self.smoothCriminalNick:
            del badNicknames[self.smoothCriminalNick.lower()]
        for canal in self.dirtyDianaChannels:
            if self in thrillerChannels[canal]:
                thrillerChannels[canal].remove(self)
                for user in thrillerChannels[canal]:
                    enviar(user.socket, f":{self.smoothCriminalNick} QUIT :Connection closed")
        self.socket.close()


# ==========================================
# Loop principal do servidor
# ==========================================
servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
servidor_socket.bind((HOST, PORT))
servidor_socket.listen()

moonwalkConnections.append(servidor_socket)

print(f"Chat Server escutando na porta {PORT}...")

try:
    while True:
        prontos_para_ler, _, _ = select.select(moonwalkConnections, [], [])
        for sock in prontos_para_ler:
            if sock is servidor_socket:
                cliente_socket, addr = servidor_socket.accept()
                cliente = BillieJean(cliente_socket, addr)
                moonwalkConnections.append(cliente_socket)
                cliente_socket.obj = cliente
                print(f"Conexão estabelecida com {addr}")
            else:
                try:
                    dados = sock.recv(MAX_BUFFER_SIZE)
                    if dados:
                        sock.obj.processar_dados(dados.decode())
                    else:
                        print(f"Conexão encerrada por {sock.obj.addr}")
                        sock.obj.sair()
                        moonwalkConnections.remove(sock)
                except:
                    sock.obj.sair()
                    moonwalkConnections.remove(sock)
except KeyboardInterrupt:
    print("\nEncerrando servidor...")
    for sock in moonwalkConnections:
        if sock != servidor_socket:
            sock.close()
    servidor_socket.close()
