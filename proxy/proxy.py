import io
import socket
import urllib.request
import time

import socks
import stem.process
from stem.util import term

SOCKS_PORT = 6000

def print_bootstrap_lines(line):
    if "Bootstrapped " in line:
        print(term.format(line, term.Color.BLUE))


def getaddrinfo(*args):
    "Let us do the actual DNS resolution in the SOCKS5 proxy"
    return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (args[0], args[1]))]

def main():
    # Start an instance of Tor configured to only exit through USA. This prints
    # Tor's bootstrap information as it starts. Note that this likely will not
    # work if you have another Tor instance running.
    print(term.format("Starting Tor:\n", term.Attr.BOLD))

    tor_process = stem.process.launch_tor_with_config(
        config={
            "SocksPort": f"0.0.0.0:{SOCKS_PORT}",
            "ExitNodes": "{us}"
        },
        init_msg_handler=print_bootstrap_lines,
    )

    socks.set_default_proxy(
        socks.PROXY_TYPE_SOCKS5, "0.0.0.0", SOCKS_PORT, False
    )
    socket.getaddrinfo = getaddrinfo
    print(term.format("Tor is running...", term.Color.GREEN))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(term.format("\nStopping Tor:\n", term.Attr.BOLD))
    finally:
        tor_process.kill()  # stops tor

if __name__ == "__main__":
    main()