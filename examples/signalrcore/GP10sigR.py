import base64
import logging
import queue
import signal
import ssl

from signalrcore.hub_connection_builder import HubConnectionBuilder
import signalrcore.hub.errors as signalrcore_err
import threading

# logging.basicConfig(level=logging.INFO, format="  > %(asctime)s [%(levelname)s:%(name)s]\t%(message)s")
log = logging.getLogger(__name__)
# log.setLevel(logging.DEBUG)


def _str_to_b64(msg):
    buffer = base64.b64encode(msg.encode("UTF-8"))
    return buffer.decode("UTF-8")


class GP10sigR(threading.Thread):
    def __init__(self,
                 host: str = "localhost",
                 port: str = "10695",
                 ssl_context: ssl.SSLContext = None,
                 auth_user: str = "admin",
                 auth_pass: str = "00000000-0000-0000-0000-000000000000",
                 event_queue: queue.Queue = queue.Queue(),
                 access_events: bool = False,
                 alarm_events: bool = False,
                 audit_events: bool = False,
                 comm_events: bool = False,
                 general_events: bool = False,
                 io_events: bool = False,
                 status_events: bool = False,
                 technical_events: bool = False):
        super().__init__()
        self.event_queue = event_queue
        enable_all = not (access_events or
                          alarm_events or
                          audit_events or
                          comm_events or
                          general_events or
                          io_events or
                          status_events or
                          technical_events)
        operations = (("AccessEventArrived", "Access", access_events or enable_all),
                      ("AlarmEventArrived", "Alarm", alarm_events or enable_all),
                      ("AuditEventArrived", "Audit", audit_events or enable_all),
                      ("CommEventArrived", "Comm", comm_events or enable_all),
                      ("GeneralEventArrived", "General", general_events or enable_all),
                      ("IOEventArrived", "IO", io_events or enable_all),
                      ("StatusUpdate", "Status", status_events or enable_all),
                      ("TechnicalEventArrived", "Technical", technical_events or enable_all))
        self.ready = threading.Event()
        self.close = threading.Event()
        self.hub_connection = HubConnectionBuilder() \
            .with_url(f"https://{host}/Hub/EventsHub",
                      ssl_context=ssl_context,
                      options={"verify_ssl": False,
                               # "access_token_factory": login_function,
                               "headers": {"Authorization": "Basic " + _str_to_b64(f"{auth_user}:{auth_pass}")}
                               }) \
            .configure_logging(logging.INFO, socket_trace=False) \
            .with_automatic_reconnect({"type": "interval",
                                       "keep_alive_interval": 10,
                                       "intervals": [1, 3, 5, 6, 7, 87, 3]
                                       }) \
            .build()

        self.hub_connection.on_open(lambda: log.info("Connection opened"))
        self.hub_connection.on_close(lambda: log.info("Connection closed"))
        self.hub_connection.on_error(lambda: log.error("Connection lost"))
        operations_enabled = []
        for operation, context, enabled in operations:
            if enabled:
                self.hub_connection.on(operation,
                                       lambda event, bound_context=context: self._push_to_queue(bound_context,
                                                                                                event[0]))
                operations_enabled.append(context)
        log.debug("Operations \"" + "\" ,\"".join(operations_enabled) + "\" enabled")

    def _push_to_queue(self, context, event):
        log.debug(f"Event \"{context}\" arrived: {event}")
        self.event_queue.put((context, event))

    def run(self):
        log.debug("Starting SignalR service")
        try:
            self.hub_connection.start()
            self.close.wait()
        except signalrcore_err.HubConnectionError:
            log.critical("API Hub Connection Error", exc_info=False)
        except signalrcore_err.UnAuthorizedHubError:
            log.error("API Authorisation Failed", exc_info=False)
        except signalrcore_err.HubError as e:
            log.error(f"API Connection Failed with status code {e}")
        finally:
            log.debug("Stopping SignalR service")
            self.hub_connection.stop()

    def stop(self, *_):
        self.close.set()


if __name__ == "__main__":
    # q = queue.Queue()

    SigR = GP10sigR()
    signal.signal(signal.SIGINT, SigR.stop)
    SigR.start()
    while True:
        while not SigR.event_queue.empty():
            log.info(SigR.event_queue.get(block=False))
