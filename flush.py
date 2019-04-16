from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import re
import logging
import subprocess

class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def _set_err(self, code=500):
        self.send_response(code)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

    def parse_query(self, query):
        querydict = {}
        q = query.split('&')
        for param in q:
            key, value = param.split('=')
            querydict[key] = value
        return querydict

    def do_GET(self):
        ip_pattern = re.compile("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$")
        logging.info("GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers))
        parse_result = urlparse(self.path)

        if parse_result.path != '/flush':
            self._set_err(404)
            self.wfile.write("Not found".encode('utf-8'))
            return

        querydict = self.parse_query(parse_result.query)
        try:
            ip = querydict['ip']
            port = int(querydict['port'])
            if port >= 65536 or port < 1:
                raise AssertionError
            if not ip_pattern.match(ip):
                raise AssertionError
            command = f'kubectl get pod -n kube-system -l k8s-app=kube-proxy -o name | cut -c5- | xargs -I[] kubectl exec -n kube-system [] -- conntrack -D -p udp -d {ip} --dport {port}'
            popen = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = popen.communicate()
            stdout = stdout.decode('utf-8')
            stderr = stderr.decode('utf-8')
            out = f'===stdout===\n{stdout}\n===stderr===\n{stderr}'
            self._set_response()
            self.wfile.write(out.format(self.path).encode('utf-8'))
        except:
            self._set_err()
            self.wfile.write("Internal Server Error".encode('utf-8'))

def run(server_class=HTTPServer, handler_class=S, port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()