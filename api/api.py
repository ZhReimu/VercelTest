import json
from http.server import BaseHTTPRequestHandler
from ip_data import CzIp


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        cz_ip = CzIp()
        request = self.request
        if request.method == 'GET':
            try:
                ip = request.args['ip']
            except KeyError:
                ip = request.remote_addr
            return json.loads(json.dumps(
                "{'code': '200',"f"'db_info': f'{cz_ip.get_version()} 当前一共有 {cz_ip.index_count} 条记录'," "'data': {'ip': "f"{ip}," f"'city': {cz_ip.get_addr_by_ip(ip)}" "} "
            ))
