import logging
import http.client
import json
from enum import Enum
from json import JSONDecodeError
from socket import error as socket_error
from utils import Stopwatch, ConvertBase64
import time


class GuardPointAuthType(Enum):
    BASIC = 1
    BEARER_TOKEN = 2


log = logging.getLogger(__name__)


class GuardPointConnection:

    def __init__(self, host, port, auth, user, pwd, key):
        self.host = host
        self.port = port
        if not isinstance(auth, GuardPointAuthType):
            raise ValueError("Parameter authType must be instance of GuardPointAuthType")
        self.authType = auth
        self.user = user
        self.pwd = pwd
        self.key = key
        self.baseurl = f"http://{host}:{port}"
        self.token = None
        self.token_issued = 0
        self.token_expiry = 0
        log.info(f"GP10 server connection: {host}:{port}")
        self.connection = http.client.HTTPConnection(self.host, self.port)

    def query(self, method, url, body='', headers=None):
        if self.authType == GuardPointAuthType.BASIC:
            auth_str = "Basic " + ConvertBase64.encode(f"{self.user}:{self.key}")
        elif self.authType == GuardPointAuthType.BEARER_TOKEN:
            if self.token is None:
                code, body = self._new_token()
                if code != 200:
                    return code, body
            if self.token_expiry < (time.time() - (30 * 60)):  # If Token will expire within 30 minutes
                code, body = self._renew_token()
                if code != 200:
                    return code, body
            if self.token_expiry < time.time():
                code, body = self._new_token()
                if code != 200:
                    return code, body

            auth_str = f"Bearer {self.token}"
        else:
            raise NotImplementedError("Selected authentication mechanism not available.")

        return self._query(method, url, body, headers, auth_str)

    def _query(self, method, url, body='', headers=None, auth_str=None):

        headers = headers or {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        if auth_str:
            headers['Authorization'] = auth_str


        log.debug(f"Request data: host={self.host}:{self.port}, {method=}, {url=}, {headers=}, {body=}")
        timer = Stopwatch().start()
        if url[0:4] != "http":
            url = f"http://{self.host}:{self.port}/odata/{url}"

        self.connection.request(method, url, body, headers)

        timer.stop()
        response = self.connection.getresponse()
        data = response.read().decode("utf-8")
        #log.debug("Response hdrs: " + str(response.headers))
        log.debug("Response data: " + response.read().decode("utf-8"))
        log.debug(f"Response \'{response.getcode()}\' received in {timer.print()}")

        return response.getcode(), data

    def _new_token(self):
        log.info("Requesting new token")
        payload = {"username": self.user,
                   "password": self.pwd}
        url = self.baseurl + "/api/Token/"
        return self._query_token(url, payload)

    def _renew_token(self):
        log.info("Renewing token")
        payload = {"oldToken": self.token}
        url = self.baseurl + "/api/Token/RenewToken"
        return self._query_token(url, payload)

    def _query_token(self, url, payload):
        code, response_body = self._query("POST", url, json.dumps(payload))

        if code == 200:
            try:
                data = json.loads(response_body)
                self.token = data['token']
                token_dict = json.loads(ConvertBase64.decode(self.token.split(".")[1]))
                self.token_issued = token_dict['iat']
                self.token_expiry = token_dict['exp']
            except JSONDecodeError:
                response_body = None
            except Exception as e:
                log.error(e)
                response_body = None

        return code, response_body
