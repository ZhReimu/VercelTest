from http.server import BaseHTTPRequestHandler
from urllib import parse
import json

from cz_ip.ip_data import CzIp


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        cz_ip = CzIp()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        query = parse.urlparse(self.path).query
        if "ip" == query[:2]:
            ip = query[3:]
        else:
            ip = self.client_address[0]

        code = 200
        db_info = f'{cz_ip.get_version()} 当前一共有 {cz_ip.index_count} 条记录'
        data = {"ip": ip, "city": cz_ip.get_addr_by_ip(ip)}

        self.wfile.write(json.dumps(
            {'code': code, 'db_info': db_info, 'data': data},
            ensure_ascii=False).encode('utf-8'))
