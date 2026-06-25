import json
import subprocess
from http.server import HTTPServer
from server import WifiServer


def wifi_connected():
    try:
        state = subprocess.check_output(
            ["nmcli", "-t", "-f", "STATE", "general"],
            text=True
        ).strip()

        return state == "connected"

    except:
        return False


def get_wifi_interface():
    output = subprocess.check_output(
        ["nmcli", "-t", "-f", "DEVICE,TYPE", "device"],
        text=True
    )

    for line in output.splitlines():
        device, dev_type = line.split(":")
        if dev_type == "wifi":
            return device

    raise RuntimeError("No Wi-Fi interface found")


def get_wifi_networks():

    output = subprocess.check_output(
        [
            "nmcli",
            "-t",
            "-f",
            "SSID,SIGNAL",
            "device",
            "wifi",
            "list",
        ],
        text=True,
    )

    networks = []

    for line in output.splitlines():

        if ":" not in line:
            continue

        ssid, signal = line.rsplit(":", 1)

        if not ssid.strip():
            continue

        networks.append(
            {
                "ssid": ssid,
                "signal": signal,
            }
        )

    

    return networks


def start_hotspot():

    iface = get_wifi_interface()
    # starting hotspot 
    subprocess.run(
        [
            "nmcli",
            "device",
            "wifi",
            "hotspot",
            "ifname",
            iface,
            "ssid",
            "BUX Wifi Setup",
            "password",
            "rushaad123",
        ],
        check=True,
    )

    # configuring hotspot settings
    subprocess.run(
        [
            "nmcli",
            "connection",
            "modify",
            "Hotspot",
            "ipv4.addresses",
            "192.168.50.1/24",
        ]
    )

    subprocess.run(
        [
            "nmcli",
            "connection",
            "modify",
            "Hotspot",
            "ipv4.method",
            "shared",
        ]
    )

    subprocess.run(
        [
            "nmcli",
            "connection",
            "up",
            "Hotspot",
        ]
    )

# stoping hotspot
def stop_hotspot():
    
    subprocess.run(
        [
            "nmcli",
            "connection",
            "down",
            "Hotspot",
        ]
    )


if wifi_connected():
    print("Already connected to Wi-Fi.")
    exit()

    print("Scanning Wi-Fi...")
    scaned_networks = get_wifi_networks()

    print("Starting hotspot...")
    start_hotspot()

    WifiServer.networks = scaned_networks

    server = HTTPServer(("0.0.0.0", 8080), WifiServer)

    print("Open http://192.168.50.1:8080")

    server.serve_forever()

    stop_hotspot()

    print("Finished")
