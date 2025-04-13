import socket
import configparser
import os

# === Caminhos Globais ===
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARQUIVOS_DIR = os.path.join(BASE_DIR, "arquivos_teste")
CONFIG_PATH = os.path.join(BASE_DIR, "config")
VALID_FILES = ["a.txt", "b.txt"]

def carregar_config(path):
    config = configparser.ConfigParser()
    config.read(path)

    return {
        "UDP_NEGOTIATION_PORT": int(config["SERVER_CONFIG"]["UDP_NEGOTIATION_PORT"]),
        "TCP_TRANSFER_PORT": int(config["SERVER_CONFIG"]["TCP_TRANSFER_PORT"])
    }

def validar_requisicao(mensagem):
    """Valida o formato da mensagem e extrai os campos."""
    try:
        comando, protocolo, arquivo = mensagem.split(",")
        return comando.strip(), protocolo.strip(), arquivo.strip()
    except ValueError:
        return None, None, None

def montar_resposta(comando, protocolo, arquivo, tcp_port):
    """Gera a resposta com base na solicitação."""
    caminho_arquivo = os.path.join(ARQUIVOS_DIR, arquivo)

    if comando != "REQUEST":
        return "ERROR,COMANDO INVALIDO,,"
    if protocolo != "TCP":
        return "ERROR,PROTOCOLO INVALIDO,,"
    if arquivo not in VALID_FILES or not os.path.isfile(caminho_arquivo):
        return "ERROR,ARQUIVO NAO ENCONTRADO,,"
    
    return f"RESPONSE,{protocolo},{tcp_port},{arquivo}"

def iniciar_servidor_udp(udp_port, tcp_port):
    """Inicia o servidor UDP para negociação inicial."""
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("0.0.0.0", udp_port))
    print(f"[Servidor] Aguardando na porta UDP {udp_port}...")

    while True:
        data, client_address = udp_socket.recvfrom(1024)
        message = data.decode().strip()
        print(f"[Servidor] Recebido de {client_address}: {message}")

        comando, protocolo, arquivo = validar_requisicao(message)

        if not comando:
            resposta = "ERROR,FORMATO INVALIDO,,"
        else:
            resposta = montar_resposta(comando, protocolo, arquivo, tcp_port)

        print(f"[Servidor] Enviando: {resposta}")
        udp_socket.sendto(resposta.encode(), client_address)

def main():
    config_path = os.path.join(BASE_DIR, "config.ini")  
    config = carregar_config(config_path)

    udp_port = config["UDP_NEGOTIATION_PORT"]
    tcp_port = config["TCP_TRANSFER_PORT"]

    iniciar_servidor_udp(udp_port, tcp_port)

if __name__ == "__main__":
    main()