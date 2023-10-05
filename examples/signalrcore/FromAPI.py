import base64
import logging
from signalrcore.hub_connection_builder import HubConnectionBuilder
import signalrcore.hub.errors as signalrcore_err
from websocket import WebSocketConnectionClosedException
import signal

server_url = "http://localhost:10695/Hub/EventsHub"
# server_url = "http://johnspc:10695/Hub/EventsHub"
# server_url = "http://sensoraccess.duckdns.org:10695/Hub/EventsHub"
# server_url = "http://192.168.1.205:10695/Hub/EventsHub"
auth_user = "admin"
auth_pass = "00000000-0000-0000-0000-000000000000"


def str_to_b64(msg):
    buffer = base64.b64encode(msg.encode("UTF-8"))
    return buffer.decode("UTF-8")


logging.basicConfig(level=logging.INFO, format="  > %(asctime)s [%(levelname)s: %(name)s]\t%(message)s")
log = logging.getLogger("main")
log.setLevel(logging.DEBUG)

print('''
  ███████╗███████╗███╗   ██╗███████╗ ██████╗ ██████╗      █████╗  ██████╗ ██████╗███████╗███████╗███████╗
  ██╔════╝██╔════╝████╗  ██║██╔════╝██╔═══██╗██╔══██╗    ██╔══██╗██╔════╝██╔════╝██╔════╝██╔════╝██╔════╝
  ███████╗█████╗  ██╔██╗ ██║███████╗██║   ██║██████╔╝    ███████║██║     ██║     █████╗  ███████╗███████╗
  ╚════██║██╔══╝  ██║╚██╗██║╚════██║██║   ██║██╔══██╗    ██╔══██║██║     ██║     ██╔══╝  ╚════██║╚════██║
  ███████║███████╗██║ ╚████║███████║╚██████╔╝██║  ██║    ██║  ██║╚██████╗╚██████╗███████╗███████║███████║
  ╚══════╝╚══════╝╚═╝  ╚═══╝╚══════╝ ╚═════╝ ╚═╝  ╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝╚══════╝╚══════╝╚══════╝

  GP10 Push-Events API Demo
  Press Return to exit

  =======================================================================================================

''')

log.info(f"Opening connection to {server_url}...")

hub_connection = HubConnectionBuilder() \
    .with_url(server_url, options={
        "verify_ssl": False,
        # "access_token_factory": login_function,
        "headers": {
            "Authorization": "Basic " + str_to_b64(f"{auth_user}:{auth_pass}")
        }
    }) \
    .configure_logging(logging.INFO, socket_trace=False) \
    .with_automatic_reconnect({
        "type": "interval",
        "keep_alive_interval": 10,
        "intervals": [1, 3, 5, 6, 7, 87, 3]
    }) \
    .build()

hub_connection.on_open(lambda: log.info("Connection opened and handshake received"))
hub_connection.on_close(lambda: log.info("Connection closed"))
hub_connection.on_error(lambda: log.info("Connection lost"))

hub_connection.on("AccessEventArrived", lambda x: log.info(f"AccessEventArrived: {x}"))
# hub_connection.on("AlarmEventArrived", lambda x: log.info(f"AlarmEventArrived: {x}"))
# hub_connection.on("AuditEventArrived", lambda x: log.info(f"AuditEventArrived: {x}"))
# hub_connection.on("CommEventArrived", lambda x: log.info(f"CommEventArrived: {x}"))
# hub_connection.on("GenaralEventArrived", lambda x: log.info(f"GenaralEventArrived: {x}"))
# hub_connection.on("IOEventArrived", lambda x: log.info(f"IOEventArrived: {x}"))
# hub_connection.on("StatusUpdate", lambda x: log.info(f"StatusUpdate: {x}"))
# hub_connection.on("TechnicalEventArrived", lambda x: log.info(f"TechnicalEventArrived: {x}"))


try:
    hub_connection.start()
    message = input("")
except signalrcore_err.HubConnectionError as e:
    log.critical("API Hub Connection Error", exc_info=False)
except signalrcore_err.UnAuthorizedHubError:
    log.error("API Authorisation Failed", exc_info=False)
except signalrcore_err.HubError as e:
    log.error(f"API Connection Failed with status code {e}")
except KeyboardInterrupt:
    pass
finally:
    hub_connection.stop()

log.info("Exit")
