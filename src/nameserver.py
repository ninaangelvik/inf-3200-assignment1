#!/usr/bin/env python
import argparse
import re
import signal
import threading

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer


node_addresses = []

class NameserverHttpHandler(BaseHTTPRequestHandler):

    def do_PUT(self):
        # URL path component is address. Just strip leading slash.
        newaddress = re.sub(r'/?([a-zA-Z0-9.-]+:\d+)', r'\1', self.path)
        node_addresses.append(newaddress)

        # Send OK response
        self.send_response(200)
        self.end_headers()


    def do_GET(self):
        # Send OK headers
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()

        # Respond with list of node addresses
        self.wfile.write("\n".join(sorted(set(node_addresses))))


def parse_args():
    PORT_DEFAULT = 8000
    DIE_AFTER_SECONDS_DEFAULT = 20 * 60
    parser = argparse.ArgumentParser(prog="nameserver", description="DHT Nameserver")

    parser.add_argument("-p", "--port", type=int, default=PORT_DEFAULT,
            help="port number to listen on, default %d" % PORT_DEFAULT)

    parser.add_argument("--die-after-seconds", type=float,
            default=DIE_AFTER_SECONDS_DEFAULT,
            help="kill server after so many seconds have elapsed, " +
                "in case we forget or fail to kill it, " +
                "default %d (%d minutes)" % (DIE_AFTER_SECONDS_DEFAULT, DIE_AFTER_SECONDS_DEFAULT/60))

    return parser.parse_args()


if __name__ == "__main__":

    args = parse_args()

    server = HTTPServer(('', args.port), NameserverHttpHandler)

    def run_server():
        print "Starting server on port" , args.port
        server.serve_forever()
        print "Server has shut down"

    def shutdown_server_on_signal(signum, frame):
        print "We get signal (%s). Asking server to shut down" % signum
        server.shutdown()

    # Start server in a new thread, because server HTTPServer.serve_forever()
    # and HTTPServer.shutdown() must be called from separate threads
    thread = threading.Thread(target=run_server)
    thread.daemon = True
    thread.start()

    # Shut down on kill (SIGTERM) and Ctrl-C (SIGINT)
    signal.signal(signal.SIGTERM, shutdown_server_on_signal)
    signal.signal(signal.SIGINT, shutdown_server_on_signal)

    # Wait on server thread, until timeout has elapsed
    #
    # Note: The timeout parameter here is also important for catching OS
    # signals, so do not remove it.
    #
    # Having a timeout to check for keeps the waiting thread active enough to
    # check for signals too. Without it, the waiting thread will block so
    # completely that it won't respond to Ctrl-C or SIGTERM. You'll only be
    # able to kill it with kill -9.
    thread.join(args.die_after_seconds)
    if thread.isAlive():
        print "Reached %.3f second timeout. Asking server to shut down" % args.die_after_seconds
        server.shutdown()

    print "Exited cleanly"
