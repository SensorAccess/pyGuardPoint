from ..guardpoint_dataclasses import ParkingGroup, Network
from .._action_helpers import resolve_uid, raise_for_error, value_list, single_entity


class ParkingGroupsAPI:

    async def get_parking_groups(self, offset: int = 0, limit: int = 40):
        """List parking groups (``API_ParkingGroups``). Returns ``list[ParkingGroup]``."""
        url = f"/odata/API_ParkingGroups?$top={int(limit)}&$skip={int(offset)}"
        return [ParkingGroup(x) for x in value_list(await self._gp_call("GET", url))]


class NetworksAPI:

    async def get_networks(self, offset: int = 0, limit: int = 40):
        """List controller networks (``API_Networks``). Returns ``list[Network]``."""
        url = f"/odata/API_Networks?$top={int(limit)}&$skip={int(offset)}"
        return [Network(x) for x in value_list(await self._gp_call("GET", url))]

    async def get_network(self, network_uid):
        """Fetch one network. Returns ``Network`` or ``None`` if not found."""
        uid = resolve_uid(network_uid, "network")
        code, json_body = await self.gp_json_query("GET", url=f"/odata/API_Networks({uid})")
        if code == 404:
            return None
        raise_for_error(code, json_body)
        entity = single_entity(json_body)
        return Network(entity) if entity else None
