import logging
import validators
from pysignalr.client import SignalRClient
from .CustomWebsocketTransport import CustomWebsocketTransport, DEFAULT_PING_INTERVAL, DEFAULT_CONNECTION_TIMEOUT, \
    DEFAULT_MAX_SIZE
from .gp_asyncio._async_guardpoint_cardholdertypes import CardholderTypesAPI
from .gp_asyncio._async_guardpoint_controllers import ControllersAPI
from .gp_asyncio._async_guardpoint_diagnostic import DiagnosticAPI
from .gp_asyncio._async_guardpoint_ouputs import OutputsAPI
from .gp_asyncio._async_guardpoint_readers import ReadersAPI
from .gp_asyncio._async_guardpoint_scheduledmags import ScheduledMagsAPI
from .gp_asyncio._async_guardpoint_customizedfields import CustomizedFieldsAPI
from .gp_asyncio._async_guardpoint_personaldetails import PersonalDetailsAPI
from .gp_asyncio._async_guardpoint_securitygroups import SecurityGroupsAPI
from .gp_asyncio._async_guardpoint_cards import CardsAPI
from .gp_asyncio._async_guardpoint_cardholders import CardholdersAPI
from .gp_asyncio._async_guardpoint_areas import AreasAPI
from .gp_asyncio._async_guardpoint_alarms import AlarmsAPI
from .gp_asyncio._async_guardpoint_events import EventsAPI
from .gp_asyncio._async_guardpoint_departments import DepartmentsAPI
from .gp_asyncio._async_guardpoint_sites import SitesAPI
from .gp_asyncio._async_guardpoint_genericinformation import GenericInfoAPI
from .gp_asyncio.guardpoint_connection_asyncio import GuardPointConnection, GuardPointAuthType

from .guardpoint_error import GuardPointError, GuardPointUnauthorized
from .guardpoint_utils import url_parser, ConvertBase64

log = logging.getLogger(__name__)


class GuardPointAsyncIO(GuardPointConnection, CardsAPI, CardholdersAPI, AreasAPI, SecurityGroupsAPI,
                        CustomizedFieldsAPI, PersonalDetailsAPI, ScheduledMagsAPI, CardholderTypesAPI,
                        OutputsAPI, DiagnosticAPI, ReadersAPI, ControllersAPI, AlarmsAPI, EventsAPI,
                        DepartmentsAPI, SitesAPI, GenericInfoAPI):
    """
    Asynchronous interface for interacting with the GuardPoint system, providing various APIs for managing cards,
    cardholders, areas, security groups, customized fields, personal details, scheduled mags, cardholder types,
    outputs, diagnostics, readers, controllers, alarms, and events.

    This class extends multiple API interfaces and provides methods for asynchronous operations.

    :param host: The host address of the GuardPoint server. Defaults to "localhost".
    :type host: str, optional
    :param port: The port number of the GuardPoint server. Defaults to None.
    :type port: int, optional
    :param auth: The authentication type to use. Defaults to GuardPointAuthType.BEARER_TOKEN.
    :type auth: GuardPointAuthType, optional
    :param username: The username for authentication. Defaults to "admin".
    :type username: str, optional
    :param pwd: The password for authentication. Defaults to "admin".
    :type pwd: str, optional
    :param key: The key for authentication. Defaults to "00000000-0000-0000-0000-000000000000".
    :type key: str, optional
    :param token: The token for authentication. Defaults to None.
    :type token: str, optional
    :param cert_file: The path to the certificate file. Defaults to None.
    :type cert_file: str, optional
    :param key_file: The path to the key file. Defaults to None.
    :type key_file: str, optional
    :param key_pwd: The password for the key file. Defaults to an empty string.
    :type key_pwd: str, optional
    :param ca_file: The path to the CA file. Defaults to None.
    :type ca_file: str, optional
    :param timeout: The timeout for connections. Defaults to 5 seconds.
    :type timeout: int, optional
    :param p12_file: The path to the PKCS#12 file. Defaults to None.
    :type p12_file: str, optional
    :param p12_pwd: The password for the PKCS#12 file. Defaults to an empty string.
    :type p12_pwd: str, optional

    :ivar task: Placeholder for an asynchronous task.
    :vartype task: asyncio.Task, optional

    :example:
        > guard_point = GuardPointAsyncIO(host="192.168.1.1", username="user", pwd="pass")
        > cardholder_count = await guard_point.get_cardholder_count()
        > print(cardholder_count)
    """
    task = None

    def __init__(self, **kwargs):
        # Set default values if not present
        host = kwargs.get('host', "localhost")
        port = kwargs.get('port', None)
        url_components = url_parser(host)
        if url_components['host'] == '':
            url_components['host'] = url_components['path']
            url_components['path'] = ''
        if port:
            url_components['port'] = port
        auth = kwargs.get('auth', GuardPointAuthType.BEARER_TOKEN)
        user = kwargs.get('username', "admin")
        pwd = kwargs.get('pwd', "admin")
        key = kwargs.get('key', "00000000-0000-0000-0000-000000000000")
        token = kwargs.get('token', None)
        certfile = kwargs.get('cert_file', None)
        keyfile = kwargs.get('key_file', None)
        key_pwd = kwargs.get('key_pwd', "")
        cafile = kwargs.get('ca_file', None)
        timeout = kwargs.get('timeout', 5)
        p12_file = kwargs.get('p12_file', None)
        p12_pwd = kwargs.get('p12_pwd', "")

        self.site_uid = kwargs.get('site_uid', None)
        if self.site_uid is not None:
            if not validators.uuid(self.site_uid):
                raise ValueError(f'Malformed Site UID {self.site_uid}')

        super().open(url_components=url_components, auth=auth, user=user, pwd=pwd, key=key, token=token,
                         cert_file=certfile, key_file=keyfile, key_pwd=key_pwd, ca_file=cafile, timeout=timeout,
                         p12_file=p12_file, p12_pwd=p12_pwd)

    async def get_cardholder_count(self):
        """
        Asynchronously retrieves the count of cardholders from the GuardPoint system.

        This method sends a GET request to the GuardPoint API endpoint to fetch the total number of cardholders.
        It handles various error scenarios, including unauthorized access and improperly formatted responses.

        :raises GuardPointUnauthorized: If the request returns a 401 Unauthorized status code.
        :raises GuardPointError: If the request returns a non-200 status code or if the response is improperly formatted.

        :return: The total number of cardholders.
        :rtype: int
        """
        url = self.baseurl + "/odata/GetCardholdersCount"
        code, json_body = await self.gp_json_query("GET", url=url)

        if code != 200:
            error_msg = ""
            if isinstance(json_body, dict):
                if 'error' in json_body:
                    error_msg = json_body['error']

            if code == 401:
                raise GuardPointUnauthorized(f"Unauthorized - ({error_msg})")
            else:
                raise GuardPointError(f"No body - ({code})")

        # Check response body is formatted as expected
        if not isinstance(json_body, dict):
            raise GuardPointError("Badly formatted response.")
        if 'totalItems' not in json_body:
            raise GuardPointError("Badly formatted response.")

        return int(json_body['totalItems'])

    async def get_signal_client(self):
        """
        Asynchronously creates and configures a SignalR client for communication with the EventsHub.

        This method initializes a `SignalRClient` instance with the appropriate URL and sets up
        the necessary headers for authentication based on the specified authentication type.
        It also configures a custom WebSocket transport for the client.

        :return: An instance of `SignalRClient` configured with the appropriate headers and transport.
        :rtype: SignalRClient

        :raises Exception: If there is an error in obtaining the authentication token.
        """
        client = SignalRClient(self.baseurl + "/Hub/EventsHub")
        headers = {}
        if self.authType == GuardPointAuthType.BASIC:
            auth_str = "Basic " + ConvertBase64.encode(f"{self.user}:{self.key}")
        else:
            token = await self.get_token()
            auth_str = f"Bearer {token}"
        headers['Authorization'] = auth_str
        client._transport = CustomWebsocketTransport(
            url=client._url,
            ssl=self.get_ssl_context(),
            protocol=client._protocol,
            callback=client._on_message,
            headers=headers,
            ping_interval=DEFAULT_PING_INTERVAL,
            connection_timeout=DEFAULT_CONNECTION_TIMEOUT,
            max_size=DEFAULT_MAX_SIZE,
        )
        return client

    async def start_listening(self, client: SignalRClient):
        """
        Start listening for messages from the SignalR client.

        This asynchronous method initiates the listening process by calling the
        `run` method on the provided `SignalRClient` instance. It will await the
        completion of the `run` method, which is expected to handle the
        communication with the SignalR server.

        :param client: An instance of `SignalRClient` that will be used to
                       start the listening process.
        :type client: SignalRClient
        :return: The result of the `client.run()` method.
        :rtype: Any
        """
        return await client.run()

    async def stop_listening(self, client: SignalRClient):
        """
        Asynchronously stops the listening process for the given SignalR client.

        This method closes the transport layer of the provided SignalR client, effectively stopping any ongoing
        communication or listening activities.

        :param client: The SignalR client whose listening process is to be stopped.
        :type client: SignalRClient
        :return: A coroutine that completes when the transport layer is successfully closed.
        :rtype: Awaitable
        """
        return await client._transport.close()
