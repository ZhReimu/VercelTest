import json
from http.server import BaseHTTPRequestHandler
import socket
import struct


class CzIp:
    def __init__(self, db_file='./ip.dat'):
        self.f_db = open(db_file, "rb")
        bs = self.f_db.read(8)
        (self.first_index, self.last_index) = struct.unpack('II', bs)
        self.index_count = int((self.last_index - self.first_index) / 7 + 1)
        self.cur_start_ip = None
        self.cur_end_ip_offset = None
        self.cur_end_ip = None
        print(self.get_version(), " 纪录总数: %d 条 " % self.index_count)

    def str2ip(self, s):
        """
        IP字符串转换为整数IP
        :param s:
        :return:
        """
        (ip,) = struct.unpack('I', socket.inet_aton(s))
        return ((ip >> 24) & 0xff) | ((ip & 0xff) << 24) | ((ip >> 8) & 0xff00) | ((ip & 0xff00) << 8)

    def ip2str(self, ip):
        """
        整数IP转化为IP字符串
        :param ip:
        :return:
        """
        return str(ip >> 24) + '.' + str((ip >> 16) & 0xff) + '.' + str((ip >> 8) & 0xff) + '.' + str(ip & 0xff)

    def get_version(self):
        """
        获取版本信息，最后一条IP记录 255.255.255.0-255.255.255.255 是版本信息
        :return: str 当前数据库文件版本信息
        """
        s = self.get_addr_by_ip(0xffffff00)
        return s

    def _get_area_addr(self, offset=0):
        if offset:
            self.f_db.seek(offset)
        bs = self.f_db.read(1)
        (byte,) = struct.unpack('B', bs)
        if byte == 0x01 or byte == 0x02:
            p = self.get_long3()
            if p:
                return self.get_offset_string(p)
            else:
                return ""
        else:
            self.f_db.seek(-1, 1)
            return self.get_offset_string(offset)

    def _get_addr(self, offset):
        """
        获取 offset 处记录区地址信息(包含国家和地区)
        如果是中国 ip，则是 " xx 省 xx 市 xxx 地区 " 这样的形式
        (比如:"福建省 电信", "澳大利亚 墨尔本 GoldenIt 有限公司")
        :param offset: 偏移量
        :return:str 该偏移量处的 IP 信息
        """
        self.f_db.seek(offset + 4)
        bs = self.f_db.read(1)
        (byte,) = struct.unpack('B', bs)
        if byte == 0x01:  # 重定向模式1
            country_offset = self.get_long3()
            self.f_db.seek(country_offset)
            bs = self.f_db.read(1)
            (b,) = struct.unpack('B', bs)
            if b == 0x02:
                country_addr = self.get_offset_string(self.get_long3())
                self.f_db.seek(country_offset + 4)
            else:
                country_addr = self.get_offset_string(country_offset)
            area_addr = self._get_area_addr()
        elif byte == 0x02:  # 重定向模式2
            country_addr = self.get_offset_string(self.get_long3())
            area_addr = self._get_area_addr(offset + 8)
        else:  # 字符串模式
            country_addr = self.get_offset_string(offset + 4)
            area_addr = self._get_area_addr()
        return country_addr + " " + area_addr

    def dump(self, first, last):
        """
        打印数据库中索引为 first 到索引为 last (不包含 last )的记录
        :param first: 要打印的索引区间的起点
        :param last:要打印的索引区间的终点
        :return:
        """
        if last > self.index_count:
            last = self.index_count
        for index in range(first, last):
            offset = self.first_index + index * 7
            self.f_db.seek(offset)
            buf = self.f_db.read(7)
            (ip, of1, of2) = struct.unpack("IHB", buf)
            address = self._get_addr(of1 + (of2 << 16))
            print("%d %s %s" % (index, self.ip2str(ip), address))

    def _set_ip_range(self, index):
        offset = self.first_index + index * 7
        self.f_db.seek(offset)
        buf = self.f_db.read(7)
        (self.cur_start_ip, of1, of2) = struct.unpack("IHB", buf)
        self.cur_end_ip_offset = of1 + (of2 << 16)
        self.f_db.seek(self.cur_end_ip_offset)
        buf = self.f_db.read(4)
        (self.cur_end_ip,) = struct.unpack("I", buf)

    def get_addr_by_ip(self, ip):
        """
        通过ip查找其地址
        :param ip: (int or str) 要查询的 IP
        :return: str 查询到的地址
        """
        if type(ip) == str:
            ip = self.str2ip(ip)
        left = 0
        right = self.index_count - 1
        while left < right - 1:
            middle = int((left + right) / 2)
            self._set_ip_range(middle)
            if ip == self.cur_start_ip:
                left = middle
                break
            if ip > self.cur_start_ip:
                left = middle
            else:
                right = middle
        self._set_ip_range(left)
        if ip & 0xffffff00 == 0xffffff00:
            self._set_ip_range(right)
        if self.cur_start_ip <= ip <= self.cur_end_ip:
            address = self._get_addr(self.cur_end_ip_offset)
        else:
            address = "未找到该IP的地址"
        return address

    def get_ip_range(self, ip):
        """
        返回 ip 所在记录的 IP 段
        :param ip: ip(str or int) 要查询的 ip
        :return: str IP 段
        """
        if type(ip) == str:
            ip = self.str2ip(ip)
        self.get_addr_by_ip(ip)
        ip_range = self.ip2str(self.cur_start_ip) + ' - ' + self.ip2str(self.cur_end_ip)
        return ip_range

    def get_offset_string(self, offset=0):
        """
        获取文件偏移处的字符串(以'\0'结尾)
        :param offset: 偏移
        :return: str 该偏移处的字符串
        """
        if offset:
            self.f_db.seek(offset)
        bs = b''
        ch = self.f_db.read(1)
        (byte,) = struct.unpack('B', ch)
        while byte != 0:
            bs += ch
            ch = self.f_db.read(1)
            (byte,) = struct.unpack('B', ch)
        return bs.decode('gbk')

    def get_long3(self, offset=0):
        """
        3字节的数值
        :param offset: 偏移量
        :return:
        """
        if offset:
            self.f_db.seek(offset)
        bs = self.f_db.read(3)
        (a, b) = struct.unpack('HB', bs)
        return (b << 16) + a


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
