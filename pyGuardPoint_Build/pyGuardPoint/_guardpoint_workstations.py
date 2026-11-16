from .guardpoint_dataclasses import Workstation, WindowType, PeriodType, LogEventType
from ._action_helpers import value_list, resolve_uid


def _workstation_names(workstations) -> list:
    """Accept a name, a ``Workstation``, or a list of either."""
    if workstations is None:
        raise ValueError("Specify at least one workstation (name or Workstation)")
    if not isinstance(workstations, (list, tuple, set)):
        workstations = [workstations]
    names = [getattr(w, 'name', w) for w in workstations]
    if not names or not all(isinstance(n, str) and n for n in names):
        raise ValueError("Workstations must be non-empty names or Workstation objects")
    return names


def _enum_value(value, enum_cls):
    """Accept an enum member, its name, or its int value; return the member name for OData."""
    if isinstance(value, enum_cls):
        return value.name
    if isinstance(value, int):
        return enum_cls(value).name
    if isinstance(value, str) and value in enum_cls.__members__:
        return value
    raise ValueError(f"Invalid {enum_cls.__name__}: {value}")


class WorkstationsAPI:
    """
    Remote control of logged-in GP10 client workstations (``API_Workstations``).
    Every action takes ``workstations`` - a name, ``Workstation``, or a list of either.
    Only workstations currently connected to the server are listed / reachable.
    """

    def get_workstations(self):
        """Connected GP10 client workstations. Returns ``list[Workstation]``."""
        return [Workstation(x) for x in value_list(self._gp_call("GET", "/odata/API_Workstations"))]

    def get_available_sounds(self):
        """Sounds a workstation can play. Returns ``{sound_name: sound_code}``."""
        json_body = self._gp_call("GET", "/odata/API_Workstations/GetAvailableSounds")
        if not isinstance(json_body, dict):
            return {}
        keys, values = json_body.get('keys'), json_body.get('values')
        if isinstance(keys, list) and isinstance(values, list):
            return dict(zip(keys, values))
        return {k: v for k, v in json_body.items() if not k.startswith('@odata')}

    def _workstation_action(self, action: str, workstations, **params):
        body = {'workstations': _workstation_names(workstations)}
        body.update(params)
        self._gp_call("POST", f"/odata/API_Workstations/{action}", body, "Workstation Not Found")
        return True

    def workstation_login(self, workstations, username: str, password: str):
        """Log a GP10 operator into the client on the given workstation(s)."""
        return self._workstation_action("Login", workstations, username=username, password=password)

    def workstation_logout(self, workstations):
        """Log the operator out of the given workstation(s)."""
        return self._workstation_action("Logout", workstations)

    def close_workstation(self, workstations, period: int = 0, period_type=PeriodType.Seconds):
        """Close the GP10 client on the given workstation(s) after ``period`` seconds/minutes."""
        return self._workstation_action("Close", workstations, period=int(period),
                                        periodType=_enum_value(period_type, PeriodType))

    def bring_workstation_to_front(self, workstations):
        """Bring the GP10 client window to the front."""
        return self._workstation_action("BringToFront", workstations)

    def display_message(self, workstations, message: str, title: str = ""):
        """Pop up a message box in the GP10 client."""
        return self._workstation_action("DisplayMessage", workstations, message=message, title=title)

    def play_sound(self, workstations, sound_code: int):
        """Play a sound - codes from :meth:`get_available_sounds`."""
        return self._workstation_action("PlaySound", workstations, soundCode=int(sound_code))

    def log_into_events_log(self, workstations, log_data: str, log_type=LogEventType.Information):
        """Write a line into the workstation's events log."""
        return self._workstation_action("LogIntoEventsLog", workstations, logData=log_data,
                                        logType=_enum_value(log_type, LogEventType))

    def open_window(self, workstations, window, uid=None, api_key: str = None, is_floating: bool = False):
        """
        Open a GP10 client window, optionally on a specific object.

        :param window: ``WindowType`` (or its name/int), e.g. ``WindowType.CardholderPopupView``.
        :param uid: object (or UID) the window shows - e.g. a ``Cardholder`` for CardholderPopupView.
        :param api_key: alternatively, the object's API key.
        :param is_floating: open as a floating window.
        """
        window_data = {'window': _enum_value(window, WindowType), 'isFloating': bool(is_floating)}
        if uid is not None:
            window_data['uid'] = resolve_uid(uid, "window target")
        if api_key is not None:
            window_data['apiKey'] = api_key
        return self._workstation_action("OpenWindow", workstations, windowData=window_data)
