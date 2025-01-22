import re
import netaddr
from bisect import bisect
import pandas as pd

ips = []

def lookup_region(ip):
    global ips
    ip = re.sub('[a-zA-Z]', '0', ip)
    ip_int = int(netaddr.IPAddress(ip))
    
    if len(ips) == 0:
        ips = pd.read_csv("ip2location.csv")
        
    idx = bisect(ips['low'].tolist(), ip_int)
    row = ips.iloc[idx-1]
    return row['region']
    
class Filing:
    def __init__(self, html):
        dates = re.findall(r"(19[0-9][0-9]|20[0-9][0-9])-(0[1-9]|1[0-2])-(0[1-9]|1[0-9]|2[0-9]|3[0,1])", html)
        self.dates = ['-'.join(date) for date in dates]
        sic = re.search(r"SIC=(\d{4}|\d{3})", html)
        if sic is not None:
            sic = int(sic.group(1))
        self.sic = sic
        self.addresses = []
        for addr_html in re.findall('<div class=\"mailer\">([\\s\\S]+?)</div>', html):
            lines = []
            for line in re.findall('<span class=\"mailerAddress\">([\\s\\S]+?)</span>', addr_html):
                if line.strip() == '':
                    continue
                else:
                    lines.append(line.strip())
            if "\n".join(lines) == '':
                continue
            self.addresses.append("\n".join(lines))

    def state(self):
        for addr in self.addresses:
            state = re.search(r"(?<![A-Z])([A-Z]{2})\s+\d{5}",addr)
            if state is not None:
                return state.group(1)
        return state