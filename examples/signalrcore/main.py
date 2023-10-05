import logging
import signal
import sys

from pyGuardPoint_Build.pyGuardPoint import GuardPoint

# logging.getLogger().setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format="  > %(asctime)s [%(levelname)s:%(name)s]\t%(message)s")
log = logging.getLogger("main")
log.setLevel(logging.DEBUG)

from GP10sigR import GP10sigR

# GuardPoint
GP_HOST = 'https://sensoraccess.duckdns.org'
GP_USER = 'admin'
GP_PASS = 'admin'
# TLS/SSL secure connection
TLS_P12 = "C:\\Users\\john_\\OneDrive\\Desktop\\MobGuardDefault\\MobileGuardDefault.p12"
TLS_P12_PWD = "test"

sys.path.insert(1, 'pyGuardPoint_Build')
from pyGuardPoint_Build.pyGuardPoint import GuardPoint, GuardPointError
gp = GuardPoint(host=GP_HOST,
                    username=GP_USER,
                    pwd=GP_PASS,
                    p12_file=TLS_P12,
                    p12_pwd=TLS_P12_PWD)
tok = gp.get_token()

SigR = GP10sigR(host="sensoraccess.duckdns.org", ssl_context=gp.get_ssl_context())
signal.signal(signal.SIGINT, SigR.stop)
SigR.start()
SigR.join()
# while True:
#     while not SigR.event_queue.empty():
#         log.info(SigR.event_queue.get(block=False))
