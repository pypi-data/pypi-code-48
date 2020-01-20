from asset_inventory.models.server import Server
from asset_inventory.models.device import Device
from asset_inventory.models.network import Network


class Inventory:

    def __init__(self, ip, server: Server, devices: [Device], networks: [Network]):
        self.ip = ip
        self.server = server
        self.devices = devices
        self.networks = networks

    def serialize(self):
        server_serialize = self.server.serialize()
        devices_serialize = [device.serialize() for device in self.devices]
        networks_serialize = [network.serialize() for network in self.networks]

        inventory_serialize = {component: value for component, value in server_serialize.items()}
        inventory_serialize.update({'devices': devices_serialize, 'networks': networks_serialize})

        return inventory_serialize
