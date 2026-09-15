"""Local controllable endpoints for transport tests: a plain HTTP target,
an HTTP proxy (absolute-form + CONNECT, auth/refuse/silent modes), a
mini SOCKS5 server and a TLS wrapper. Everything binds 127.0.0.1 only —
no real network, no paid APIs (TASK-009 test requirements).
"""

from __future__ import annotations

import base64
import socket
import ssl
import subprocess
import threading
from pathlib import Path


def _recv_head(sock: socket.socket, limit: int = 65536) -> str:
    buf = bytearray()
    while b"\r\n\r\n" not in buf:
        chunk = sock.recv(4096)
        if not chunk:
            break
        buf.extend(chunk)
        if len(buf) > limit:
            break
    return bytes(buf).split(b"\r\n\r\n", 1)[0].decode("latin-1")


def _pump(src: socket.socket, dst: socket.socket) -> None:
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        try:
            dst.shutdown(socket.SHUT_WR)
        except OSError:
            pass


def _splice(a: socket.socket, b: socket.socket) -> None:
    """Relay both directions until EOF; blocks so the handler only
    returns (and closes) after the exchange is fully drained."""
    threads = [
        threading.Thread(target=_pump, args=(a, b), daemon=True),
        threading.Thread(target=_pump, args=(b, a), daemon=True),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=30)


class _Acceptor:
    """TCP accept loop on 127.0.0.1:<ephemeral>; handler per connection."""

    def __init__(self, handler) -> None:
        self._handler = handler
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind(("127.0.0.1", 0))
        self._sock.listen(16)
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def _loop(self) -> None:
        while True:
            try:
                conn, _addr = self._sock.accept()
            except OSError:
                return
            conn.settimeout(15)
            threading.Thread(
                target=self._handler, args=(conn,), daemon=True
            ).start()

    @property
    def port(self) -> int:
        return self._sock.getsockname()[1]

    def url(self, scheme: str = "http", path: str = "/health") -> str:
        return f"{scheme}://127.0.0.1:{self.port}{path}"

    def close(self) -> None:
        try:
            self._sock.close()
        except OSError:
            pass


class LocalTargetServer(_Acceptor):
    """Plain HTTP target recording what it received."""

    def __init__(self) -> None:
        self.requests: list[tuple[str, str, dict[str, str]]] = []
        self._lock = threading.Lock()
        super().__init__(self._serve)

    def _serve(self, conn: socket.socket) -> None:
        try:
            head = _recv_head(conn)
            lines = head.split("\r\n")
            if not lines or " " not in lines[0]:
                return  # client hung up before sending a request
            method, path, _version = lines[0].split(" ", 2)
            headers = {}
            for line in lines[1:]:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key.lower()] = value
            length = int(headers.get("content-length", "0") or 0)
            if length:
                conn.recv(length)
            with self._lock:
                self.requests.append((method, path, headers))
            forced_status = int(headers.get("x-test-status", "200") or 200)
            body = (
                b'{"server": "target", "method": "'
                + method.encode()
                + b'", "path": "'
                + path.encode()
                + b'"}'
            )
            reason = {200: b"OK", 401: b"Unauthorized", 403: b"Forbidden"}.get(
                forced_status, b"Status"
            )
            conn.sendall(
                b"HTTP/1.1 "
                + str(forced_status).encode()
                + b" "
                + reason
                + b"\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: "
                + str(len(body)).encode()
                + b"\r\n"
                b"Connection: close\r\n\r\n"
                + body
            )
        except OSError:
            pass
        finally:
            try:
                conn.close()
            except OSError:
                pass


class ControlledProxyServer(_Acceptor):
    """HTTP proxy with selectable misbehavior for failure tests.

    mode:
      - ``forward``: absolute-form requests are forwarded to the target.
      - ``tunnel``: CONNECT splices to the target.
      - ``silent``: accepts and never answers (timeout tests).
    ``require_auth`` expects ``Basic <user>:<pass>`` on the request.
    """

    def __init__(
        self,
        mode: str = "tunnel",
        *,
        username: str = "",
        password: str = "",
        refuse_status: int = 502,
    ) -> None:
        self.mode = mode
        self.username = username
        self.password = password
        self.refuse_status = refuse_status
        self.connect_targets: list[str] = []
        self.auth_failures = 0
        self.forward_auth_headers: list[str] = []
        self._lock = threading.Lock()
        super().__init__(self._serve)

    def _authed(self, headers: dict[str, str]) -> bool:
        if not self.username:
            return True
        token = headers.get("proxy-authorization", "")
        expected = base64.b64encode(
            f"{self.username}:{self.password}".encode()
        ).decode()
        return token == f"Basic {expected}"

    def _serve(self, conn: socket.socket) -> None:
        try:
            if self.mode == "silent":
                import time

                time.sleep(20)
                return
            head = _recv_head(conn)
            lines = head.split("\r\n")
            request_line = lines[0]
            headers = {}
            for line in lines[1:]:
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key.lower()] = value

            if request_line.startswith("CONNECT "):
                target = request_line.split(" ")[1]
                with self._lock:
                    self.connect_targets.append(target)
                if not self._authed(headers):
                    with self._lock:
                        self.auth_failures += 1
                    conn.sendall(
                        b"HTTP/1.1 407 Proxy Authentication Required\r\n"
                        b"Proxy-Authenticate: Basic realm=\"test\"\r\n"
                        b"Content-Length: 0\r\n\r\n"
                    )
                    return
                if self.mode == "refuse":
                    status = str(self.refuse_status).encode()
                    conn.sendall(
                        b"HTTP/1.1 "
                        + status
                        + b" Proxy Refused\r\nContent-Length: 0\r\n\r\n"
                    )
                    return
                host, _, port = target.rpartition(":")
                upstream = socket.create_connection((host, int(port)), timeout=15)
                conn.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
                _splice(conn, upstream)
                return

            # absolute-form GET http://host:port/path
            parts_of_line = request_line.split(" ")
            if len(parts_of_line) < 2 or "://" not in parts_of_line[1]:
                return  # not an absolute-form request (e.g. stray bytes)
            url = parts_of_line[1]
            if self.mode == "refuse_get":
                conn.sendall(
                    b"HTTP/1.1 502 Bad Gateway\r\nContent-Length: 0\r\n\r\n"
                )
                return
            if not self._authed(headers):
                with self._lock:
                    self.auth_failures += 1
                conn.sendall(
                    b"HTTP/1.1 407 Proxy Authentication Required\r\n"
                    b"Content-Length: 0\r\n\r\n"
                )
                return
            # record the Proxy-Authorization the client actually sent
            with self._lock:
                self.forward_auth_headers.append(
                    headers.get("proxy-authorization", "")
                )
            parts = url.split("://", 1)[1]
            hostport, _, path = parts.partition("/")
            upstream = socket.create_connection(
                tuple(hostport.rpartition(":")[::2]), timeout=15
            )
            host, _, port = hostport.rpartition(":")
            upstream.sendall(
                f"GET /{path} HTTP/1.1\r\nHost: {host}\r\n"
                "Connection: close\r\n\r\n".encode()
            )
            _pump(upstream, conn)
        except OSError:
            pass
        finally:
            try:
                conn.close()
            except OSError:
                pass


class MiniSocks5Server(_Acceptor):
    """SOCKS5 (RFC 1928/1929) with optional user/pass auth and splicing."""

    def __init__(self, *, username: str = "", password: str = "") -> None:
        self.username = username
        self.password = password
        self.requests: list[tuple[str, int]] = []
        self.auth_failures = 0
        self._lock = threading.Lock()
        super().__init__(self._serve)

    def _recv_exact(self, conn: socket.socket, count: int) -> bytes:
        buf = bytearray()
        while len(buf) < count:
            chunk = conn.recv(count - len(buf))
            if not chunk:
                raise OSError("short read")
            buf.extend(chunk)
        return bytes(buf)

    def _serve(self, conn: socket.socket) -> None:
        try:
            head = self._recv_exact(conn, 2)
            nmethods = head[1]
            methods = self._recv_exact(conn, nmethods)
            if self.username:
                if b"\x02" not in methods:
                    conn.sendall(b"\x05\xff")
                    return
                conn.sendall(b"\x05\x02")
                ver = self._recv_exact(conn, 1)
                ulen = self._recv_exact(conn, 1)[0]
                user = self._recv_exact(conn, ulen)
                plen = self._recv_exact(conn, 1)[0]
                pwd = self._recv_exact(conn, plen)
                ok = (
                    user.decode() == self.username
                    and pwd.decode() == self.password
                    and ver == b"\x01"
                )
                with self._lock:
                    if not ok:
                        self.auth_failures += 1
                conn.sendall(b"\x01" + (b"\x00" if ok else b"\x01"))
                if not ok:
                    return
            else:
                if b"\x00" not in methods:
                    conn.sendall(b"\x05\xff")
                    return
                conn.sendall(b"\x05\x00")

            req = self._recv_exact(conn, 4)
            if req[:3] != b"\x05\x01\x00":
                conn.sendall(b"\x05\x07\x00\x04" + b"\x00" * 18 + b"\x00\x00")
                return
            atyp = req[3]
            if atyp == 0x01:
                host = socket.inet_ntoa(self._recv_exact(conn, 4))
            elif atyp == 0x03:
                length = self._recv_exact(conn, 1)[0]
                host = self._recv_exact(conn, length).decode()
            elif atyp == 0x04:
                host = socket.inet_ntop(
                    socket.AF_INET6, self._recv_exact(conn, 16)
                )
            else:
                return
            port = int.from_bytes(self._recv_exact(conn, 2), "big")
            with self._lock:
                self.requests.append((host, port))
            upstream = socket.create_connection((host, port), timeout=15)
            conn.sendall(b"\x05\x00\x00\x01" + b"\x7f\x00\x00\x01" + b"\x00\x00")
            _splice(conn, upstream)
        except OSError:
            pass
        finally:
            try:
                conn.close()
            except OSError:
                pass


def make_tls_target(cert_dir: Path) -> tuple[LocalTargetServer, str]:
    """Wrap a fresh target in TLS via an openssl-generated self-signed
    cert. Returns (server, cafile-for-clients). Skips via ImportError
    semantics are handled by callers; here it raises if openssl is
    unavailable.
    """
    import shutil

    openssl = shutil.which("openssl")
    if not openssl:
        raise RuntimeError("openssl not on PATH; TLS target unavailable")

    cert = cert_dir / "cert.pem"
    key = cert_dir / "key.pem"
    if not cert.exists():
        subprocess.run(
            [
                openssl,
                "req",
                "-x509",
                "-newkey",
                "rsa:2048",
                "-keyout",
                str(key),
                "-out",
                str(cert),
                "-days",
                "2",
                "-nodes",
                "-subj",
                "/CN=127.0.0.1",
                "-addext",
                "subjectAltName=IP:127.0.0.1",
            ],
            check=True,
            capture_output=True,
        )

    plain = LocalTargetServer()
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(str(cert), str(key))

    class _TlsTarget(_Acceptor):
        def __init__(self) -> None:
            self.inner = plain
            super().__init__(self._serve)

        def _serve(self, conn: socket.socket) -> None:
            try:
                tls_conn = context.wrap_socket(conn, server_side=True)
            except (ssl.SSLError, OSError):
                try:
                    conn.close()
                except OSError:
                    pass
                return
            tls_conn.settimeout(15)
            self.inner._serve(tls_conn)  # noqa: SLF001 - test helper reuse

    return _TlsTarget(), str(cert)
