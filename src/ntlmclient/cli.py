#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = ["impacket>=0.12"]
# ///
import argparse
import base64
import contextlib
import logging
import socket
from impacket.ntlm import getNTLMSSPType1, getNTLMSSPType3

log = logging.getLogger(__name__)

def build_http_request(path: str, host: str, port: int, auth_header: str) -> bytes:
    return (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Authorization: NTLM {auth_header}\r\n"
        f"Connection: keep-alive\r\n"
        f"\r\n"
    ).encode()

def read_http_response(sock: socket.socket) -> tuple:
    data = b''
    while b'\r\n\r\n' not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    if not data:
        raise ConnectionError("Verbindung wurde ohne Antwort geschlossen")
    header_part = data.split(b'\r\n\r\n')[0].decode()
    lines = header_part.split('\r\n')
    status_line = lines[0].split(' ')
    if len(status_line) < 2 or not status_line[1].isdigit():
        raise ConnectionError(f"Keine gueltige HTTP-Statuszeile erhalten: {lines[0]!r}")
    status = int(status_line[1])
    headers = {}
    for line in lines[1:]:
        if ': ' in line:
            k, v = line.split(': ', 1)
            headers[k.lower()] = v
    return status, headers

def send_ntlm_request(username: str, password: str, domain: str, host: str, port: int, path: str):
    with contextlib.closing(socket.create_connection((host, port), timeout=10)) as sock:
        # Schritt 1: Negotiate
        type1 = getNTLMSSPType1(workstation='', domain=domain)
        type1['flags'] &= ~0x00000030
        type1_b64 = base64.b64encode(type1.getData()).decode()

        sock.sendall(build_http_request(path, host, port, type1_b64))

        # Schritt 2: Challenge lesen
        status, headers = read_http_response(sock)
        log.debug(f"Challenge Status: {status}")

        www_auth = headers.get('www-authenticate', '')
        if not www_auth.startswith('NTLM '):
            raise ValueError(f"Kein NTLM Challenge erhalten: {www_auth}")

        type2_bytes = base64.b64decode(www_auth.split(' ', 1)[1].strip())

        # Schritt 3: Authenticate
        type3, _ = getNTLMSSPType3(
            type1,
            type2_bytes,
            username,
            password,
            domain,
            use_ntlmv2=True
        )
        type3['flags'] &= ~0x00000030
        type3_b64 = base64.b64encode(type3.getData()).decode()

        sock.sendall(build_http_request(path, host, port, type3_b64))

        status, headers = read_http_response(sock)
        print(f"Status: {status}")
        print(f"Headers: {headers}")

def main():
    parser = argparse.ArgumentParser(description='NTLM Client ohne Signing')
    parser.add_argument('-u', '--username', required=True)
    parser.add_argument('-p', '--password', required=True)
    parser.add_argument('-d', '--domain',   required=True)
    parser.add_argument(      '--host',     default='127.0.0.1')
    parser.add_argument(      '--port',     default=80, type=int)
    parser.add_argument(      '--path',     default='/')
    parser.add_argument('-v', '--verbose',  action='store_true',
                        help='Debug-Logging aktivieren')
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.WARNING)

    send_ntlm_request(args.username, args.password, args.domain, args.host, args.port, args.path)

if __name__ == '__main__':
    main()
