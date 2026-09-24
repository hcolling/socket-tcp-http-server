# socket-tcp-http-server

Servidor Web desenvolvido em Python utilizando diretamente **Sockets TCP**.

## Sobre o projeto

O projeto consiste na implementação de um servidor Web capaz de receber requisições HTTP do tipo `GET`, interpretar o recurso solicitado e retornar respostas HTTP com conteúdo HTML.

O servidor utiliza:

- Python 3
- Sockets TCP
- IPv4
- HTTP/1.1
- HTML

## Integrantes

- Gabriel Pires de Farias
- Henrique Colling
- Vítor Duarte

## Estrutura do projeto

```text
socket-tcp-http-server/
├── server.py
├── http_status.py
├── README.md
└── templates/
    ├── main.html
    ├── about.html
    ├── 404.html
    └── 405.html