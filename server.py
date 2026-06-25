from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs
import subprocess
import json
import threading

class WifiServer(BaseHTTPRequestHandler):

    networks = []
        
    def do_GET(self):

        if self.path == "/":

            with open("index.html", "rb") as f:
                html = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html)

        elif self.path == "/scan":

            networks = self.networks

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()

            self.wfile.write(json.dumps(WifiServer.networks).encode())

        else:
            self.send_error(404)

    def do_POST(self):

        if self.path != "/connect":
            self.send_error(404)
            return

        length = int(self.headers["Content-Length"])

        body = self.rfile.read(length).decode()

        data = parse_qs(body)

        ssid = data["ssid"][0]

        if ssid == "__CUSTOM__":
            ssid = data["custom_ssid"][0]

        password = data["password"][0]

        try:

            subprocess.run(
                [
                    "nmcli",
                    "connection",
                    "down",
                    "Hotspot",
                ]
            )

            subprocess.run(
                [
                    "nmcli",
                    "device",
                    "wifi",
                    "rescan",
                ]
            )

            subprocess.check_call(
                [
                    "nmcli",
                    "device",
                    "wifi",
                    "connect",
                    ssid,
                    "password",
                    password,
                ]
            )

            message = f"Connected to {ssid}"

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(f"""
            <h2>{message}</h2>
            <p>You may now close this page.</p>
            """.encode())

            threading.Thread(
                target=self.server.shutdown,
                daemon=True
            ).start()

        except subprocess.CalledProcessError:

            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()

            self.wfile.write(b"""
            <h2>Connection Failed</h2>
            <a href="/">Try Again</a>
            """)
            