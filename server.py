'''
Web Server using TCP Sockets

This project implements a Web server using TCP sockets, handling HTTP GET
requests and returning HTML pages for the main route (/) and the about route
(/sobre), as well as a 404 Not Found response for non-existent resources.

Developed by: Henrique Colling, Gabriel Pires de Farias & Vítor Duarte
Semester: 2026/2

Discipline: Redes de Computadores: Aplicação e Transporte
'''

import socket
from urllib.parse import urlsplit

# Server configuration
HOST = "0.0.0.0"
PORT = 8080
BUFFER_SIZE = 4096


# HTML Pages
MAIN_PAGE = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Servidor Web</title>
</head>
<body>
	<h1>Bem-vindo ao nosso servidor Web!</h1>
	<p>Esta é a página principal do servidor desenvolvido com Sockets TCP.</p>
	<p><a href="/sobre">Conheça os conceitos de Socket, TCP e HTTP</a></p>
</body>
</html>
"""

ABOUT_PAGE = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Sobre - Servidor Web</title>
</head>
<body>
	<h1>Sobre o servidor</h1>

	<h2>Socket</h2>
	<p>
		Um Socket é uma interface de comunicação utilizada por programas
		para enviar e receber dados através de uma rede.
	</p>

	<h2>TCP</h2>
	<p>
		O TCP é um protocolo da camada de transporte que estabelece uma
		conexão e permite a entrega confiável e ordenada dos dados.
	</p>

	<h2>HTTP</h2>
	<p>
		O HTTP é um protocolo da camada de aplicação utilizado na
		comunicação entre clientes e servidores Web. Neste projeto,
		utilizamos requisições GET e respostas HTTP.
	</p>

	<p><a href="/">Voltar para a página principal</a></p>
</body>
</html>
"""

NOT_FOUND_PAGE = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
	<meta charset="UTF-8">
	<title>404 - Página não encontrada</title>
</head>
<body>
	<h1>404 - Página não encontrada</h1>
	<p>O recurso solicitado não existe neste servidor.</p>
	<p><a href="/">Voltar para a página principal</a></p>
</body>
</html>
"""

NOT_ALLOWED_PAGE = """\
<!DOCTYPE html>
<html lang="pt-BR">
<head>
	<meta charset="UTF-8">
	<title>405 - Método não permitido</title>
</head>
<body>
	<h1>405 - Método não permitido</h1>
	<p>Este servidor aceita apenas requisições GET.</p>
</body>
</html>
"""


def create_response(status, content, reason):
	"""Build a response HTTP/1.1 with headers and HTML content."""

	body = content.encode("utf-8")

	header = (
		f"HTTP/1.1 {status} {reason}\r\n"
		"Content-Type: text/html; charset=utf-8\r\n"
		f"Content-Length: {len(body)}\r\n"
		"Connection: close\r\n"
		"\r\n"
	).encode("utf-8")

	return header + body


def process_request(request):
	"""Interpret the initial line of the HTTP request."""

	lines = request.split("\r\n")
	initial_line = lines[0]

	parts = initial_line.split()

	if len(parts) != 3:
		return create_response(400,
			"<h1>400 - Requisição inválida</h1>", "Bad Request")

	method, path, version = parts

	print(f"Requisição recebida: {initial_line}")

	# The server only accepts HTTP/1.1 and HTTP/1.0.
	if version not in ("HTTP/1.1", "HTTP/1.0"):
		return create_response(400,
			"<h1>400 - Versão HTTP não suportada</h1>", "Bad Request")

	# The assignment requires handling only GET requests.
	if method != "GET":
		return create_response(405, NOT_ALLOWED_PAGE, "Method Not Allowed")

	# Ignore URL parameters, like /sobre?origem=menu.
	path = urlsplit(path).path

	# Identify the requested resource.
	if path == "/":
		return create_response(200, MAIN_PAGE, "OK")

	elif path == "/sobre":
		return create_response(200, ABOUT_PAGE, "OK")

	else:
		return create_response(404, NOT_FOUND_PAGE, "Not Found")


def handle_client(client, address):
	"""Receive a request and send the response to the client."""

	try:
		client.settimeout(5)

		data = b""

		# Receive data until the end of the HTTP headers is found.
		while b"\r\n\r\n" not in data:
			block = client.recv(BUFFER_SIZE)

			if not block:
				break

			data += block

			# Avoid receiving excessively large headers.
			if len(data) > 65536:
				break

		if not data:
			return

		request = data.decode("iso-8859-1")

		print("-" * 50)
		print(f"Cliente conectado: {address[0]}:{address[1]}")
		print("Requisição HTTP completa:")
		print(request.rstrip())
		print("-" * 50)

		response = process_request(request)

		# Send the HTTP headers and HTML content.
		client.sendall(response)

	except socket.timeout:
		# print("Tempo limite excedido ao receber a requisição.")
		pass

	except OSError as error:
		print(f"Erro na comunicação com o cliente: {error}")

	finally:
		client.close()


def init_server():
	"""Create the TCP Socket and start the Web server."""

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Allows reusing the port after restarting the server.
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		# Bind the Socket to the address and port.
		server.bind((HOST, PORT))

		# Place the Socket in listening mode.
		server.listen()

		print("=" * 50)
		print("Servidor Web iniciado!")
		print(f"Acesse: http://localhost:{PORT}")
		print(f"Ou:     http://127.0.0.1:{PORT}")
		print("Pressione Ctrl+C para encerrar.")
		print("=" * 50)

		# Keep the server running, waiting for clients.
		while True:
			client, address = server.accept()

			# Handle one connection at a time.
			handle_client(client, address)

	except KeyboardInterrupt:
		print("\nServidor encerrado pelo usuário.")

	except OSError as error:
		print(f"Erro ao iniciar ou executar o servidor: {error}")

	finally:
		server.close()
		print("Socket do servidor fechado.")


if __name__ == "__main__":
	init_server()
