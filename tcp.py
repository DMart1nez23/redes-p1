import socket
import asyncio

class Rede:
    def __init__(self, porta_escuta):
        canal = self.canal = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        canal.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        canal.bind(('', porta_escuta))
        canal.listen(5)

    def definir_callback_conexao(self, manipulador):
        loop = asyncio.get_event_loop()
        loop.add_reader(self.canal, lambda: manipulador(Enlace(self.canal.accept())))

class Enlace:
    def __init__(self, tupla_aceita):
        self.canal, _ = tupla_aceita

    def ativar_escuta(self, manipulador):
        loop = asyncio.get_event_loop()
        loop.add_reader(self.canal, lambda: manipulador(self, self.canal.recv(8192)))

    def transmitir(self, pacote):
        self.canal.sendall(pacote)

    def desconectar(self):
        loop = asyncio.get_event_loop()
        loop.remove_reader(self.canal)
        self.canal.close()
