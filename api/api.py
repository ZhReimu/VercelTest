import json
from urllib import parse
from http.server import BaseHTTPRequestHandler
from api.ip_data import CzIp


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        cz_ip = CzIp()
        self.send_response(200)
        self.end_headers()

        query = parse.urlparse(self.path).query
        if "ip" == query[:2]:
            ip = query[3:]
        else:
            ip = self.client_address[0]
        code = 200
        db_info = f'{cz_ip.get_version()} 当前一共有 {cz_ip.index_count} 条记录'
        data = str({'ip': ip, 'city': cz_ip.get_addr_by_ip(ip)})

        self.wfile.write(json.loads(json.dumps(
            '{' + f'code: {code},\'db_info:{db_info},\'data\':{data} ' + '}'
        )).encode('utf-8'))
