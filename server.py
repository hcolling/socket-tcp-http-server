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
from pathlib import Path
from urllib.parse import urlsplit
from http_status import HTTPStatus

# Server configuration
HOST = "0.0.0.0"
PORT = 8080
BUFFER_SIZE = 4096
MAX_HEADER_SIZE = 65536
EXPECTED_REQUEST_PARTS = 3
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"

def load_template(filename):
    """Read and return the content of an HTML template file."""
    template_path = TEMPLATES_DIR / filename
    return template_path.read_text(encoding="utf-8")

# HTML Pages
MAIN_PAGE = load_template("main.html")
ABOUT_PAGE = load_template("about.html")
NOT_FOUND_PAGE = load_template("404.html")
NOT_ALLOWED_PAGE = load_template("405.html")


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

	if len(parts) != EXPECTED_REQUEST_PARTS:
		return create_response(HTTPStatus.BAD_REQUEST,
			"<h1>400 - Requisição inválida</h1>", "Bad Request")

	method, path, version = parts

	print(f"Requisição recebida: {initial_line}")

	# The server only accepts HTTP/1.1 and HTTP/1.0.
	if version not in ("HTTP/1.1", "HTTP/1.0"):
		return create_response(HTTPStatus.BAD_REQUEST,
			"<h1>400 - Versão HTTP não suportada</h1>", "Bad Request")

	# The assignment requires handling only GET requests.
	if method != "GET":
		return create_response(HTTPStatus.METHOD_NOT_ALLOWED, NOT_ALLOWED_PAGE, "Method Not Allowed")

	# Ignore URL parameters, like /sobre?origem=menu.
	path = urlsplit(path).path

	# Identify the requested resource.
	if path == "/":
		return create_response(HTTPStatus.OK, MAIN_PAGE, "OK")

	elif path == "/sobre":
		return create_response(HTTPStatus.OK, ABOUT_PAGE, "OK")

	else:
		return create_response(HTTPStatus.NOT_FOUND, NOT_FOUND_PAGE, "Not Found")


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
			if len(data) > MAX_HEADER_SIZE:
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
