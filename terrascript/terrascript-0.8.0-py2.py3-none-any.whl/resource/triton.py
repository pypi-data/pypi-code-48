# terrascript/resource/triton.py

import terrascript


class triton_fabric(terrascript.Resource):
    pass

class triton_firewall_rule(terrascript.Resource):
    pass

class triton_instance_template(terrascript.Resource):
    pass

class triton_key(terrascript.Resource):
    pass

class triton_machine(terrascript.Resource):
    pass

class triton_service_group(terrascript.Resource):
    pass

class triton_snapshot(terrascript.Resource):
    pass

class triton_vlan(terrascript.Resource):
    pass


__all__ = [
    'triton_fabric',
    'triton_firewall_rule',
    'triton_instance_template',
    'triton_key',
    'triton_machine',
    'triton_service_group',
    'triton_snapshot',
    'triton_vlan',
]