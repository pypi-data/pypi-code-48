from paradox.event import EventLevel, LiveEvent


def _toggle_provider(old):
    return not old


def _minor2_provider(event, *_):
    return event.minor2


def _request_status_refresh(alarm, *_, **__):
    alarm.request_status_refresh()


def _zone_generated_alarm(event, storage, *_, **__):
    assert isinstance(event, LiveEvent)
    storage.update_container_object('partition', event.partition, {
        "current_state": "triggered",
        "alarm_in_memory": True,
        "was_in_alarm": True,
        "audible_alarm": True,
        "exit_delay": False
    })


event_map = {
    0: dict(
        level=EventLevel.DEBUG, change=dict(open=False), type='zone', message='Zone {label} OK'),
    1: dict(
        level=EventLevel.DEBUG, change=dict(open=True), type='zone', message='Zone {label} open'),
    2: dict(
        level=EventLevel.WARN, tags=['trouble'], change=dict(zone_tamper_trouble=True), type='zone',
        message='Zone {label} tampered'),
    3: dict(
        level=EventLevel.WARN, tags=['trouble'], type='zone', change=dict(fire_loop_trouble=True),
        message='Zone {label} in fire loop trouble'),
    4: dict(
        level=EventLevel.DEBUG, message='Non-reportable event',
        sub={
            0: dict(level=EventLevel.CRITICAL, type='system', tags=['trouble'], message='Telephone line trouble'),
            1: dict(type='system', message='Smoke detector reset'),
            2: dict(level=EventLevel.INFO, tags=['arm'], type='partition', change=dict(arm=True),
                    message='Arm with no entry delay'),
            3: dict(level=EventLevel.INFO, tags=['arm'], type='partition', change=dict(arm_stay=True, arm=True),
                    message='Arm in stay mode'),
            4: dict(level=EventLevel.INFO, tags=['arm'], type='partition', change=dict(arm_away=True, arm=True),
                    message='Arm in Away mode'),
            5: dict(level=EventLevel.INFO, tags=['arm'], type='partition', change=dict(arm_stay=True, arm=True),
                    message='Full arm when in Stay mode'),
            6: dict(type='system', message='Voice module access'),
            7: dict(type='system', message='Remote control access by {@user}', user=_minor2_provider),
            8: dict(type='system', message='PC fail to communicate'),
            9: dict(type='system', message='Midnight'),
            10: dict(type='system', message='Neware user login'),
            11: dict(type='system', message='Neware user logout'),
            12: dict(type='system', message='User initiated call-up'),
            13: dict(type='system', message='Force answer'),
            14: dict(type='system', message='Force hangup'),
            15: dict(type='system', message='Reset to default'),
            16: dict(type='system', message='Auxiliary output manually activated'),
            17: dict(type='system', message='Auxiliary output manually deactivated'),
            18: dict(type='system', message='Voice reporting failed'),
            19: dict(type='system', message='Fail to communicate restore', telephone=_minor2_provider),
            20: dict(type='system', message='Software access (VDMP3, Ip100, Neware, WinLoad)'),  # minor2 has sub events
            21: dict(type='system', message='IPR512 1 registration status'),
            22: dict(type='system', message='IPR512 2 registration status'),
            23: dict(type='system', message='IPR512 3 registration status'),
            24: dict(type='system', message='IPR512 4 registration status')
        }),
    5: dict(
        level=EventLevel.INFO, type='user', message='User {label} code entered on keypad', keypad=_minor2_provider),
    6: dict(
        level=EventLevel.INFO, type='door', message='User/card access on door {label}', user=_minor2_provider),
    7: dict(
        level=EventLevel.INFO, type='user', message='Bypass programming access'),
    8: dict(
        level=EventLevel.WARN, type='zone', message='TX delay zone {label} alarm'),
    9: dict(
        level=EventLevel.INFO, tags=['arm'], change=dict(arm=True), type='partition',
        message='Arming {label} with master code'),
    10: dict(
        level=EventLevel.INFO, tags=['arm'], change=dict(arm=True), type='partition',
        message='Arming {label} with user code'),
    11: dict(
        level=EventLevel.INFO, tags=['arm'], change=dict(arm=True), type='partition',
        message='Arming {label} with keyswitch'),
    12: dict(
        level=EventLevel.INFO, tags=['arm'], change=dict(arm=True), type='partition', message='Special arming {label}',
        sub={  # no label passed
            0: dict(type='partition', message='auto arming'),
            1: dict(type='partition', message='arming with Winload by {@user}', user=_minor2_provider),
            2: dict(type='partition', message='late to close'),
            3: dict(type='partition', message='no movement arming'),
            4: dict(type='partition', message='partial arming'),
            5: dict(type='partition', message='one-touch arming'),
            6: dict(type='partition', message='Future use 1'),
            7: dict(type='partition', message='Future use 2'),
            8: dict(type='partition', message='(InTouch) voice module arming'),
            9: dict(type='partition', message='Delinquency c;psomg'),
            10: dict(type='partition', message='Future use 3'),
        }),
    13: dict(
        level=EventLevel.INFO, tags=['disarm'], change=dict(arm=False, current_state="disarmed", audible_alarm=False),
        type='partition', message='{label} disarmed with master'),
    14: dict(
        level=EventLevel.INFO, tags=['disarm'], change=dict(arm=False, current_state="disarmed", audible_alarm=False),
        type='partition', message='{label} disarmed with user code'),
    15: dict(
        level=EventLevel.INFO, tags=['disarm'], change=dict(arm=False, current_state="disarmed", audible_alarm=False),
        type='partition', message='{label} disarmed with keyswitch'),
    16: dict(
        level=EventLevel.INFO, tags=['disarm', 'after_alarm'],
        change=dict(arm=False, current_state="disarmed", audible_alarm=False), type='partition',
        message='{label} disarmed after alarm with master'),
    17: dict(
        level=EventLevel.INFO, tags=['disarm', 'after_alarm'],
        change=dict(arm=False, current_state="disarmed", audible_alarm=False), type='partition',
        message='{label} disarmed after alarm with user code'),
    18: dict(
        level=EventLevel.INFO, tags=['disarm', 'after_alarm'],
        change=dict(arm=False, current_state="disarmed", audible_alarm=False), type='partition',
        message='{label} disarmed after alarm with keyswitch'),
    19: dict(
        level=EventLevel.INFO, tags=['alarm', 'cancel'], type='user', message='Alarm cancelled by {label} (master)'),
    20: dict(
        level=EventLevel.INFO, tags=['alarm', 'cancel'], type='user', message='Alarm cancelled by {label} (user code)'),
    21: dict(
        level=EventLevel.INFO, tags=['alarm', 'cancel'], type='keyswitch',
        message='{label} Alarm cancelled with keyswitch'),
    22: dict(
        level=EventLevel.INFO, tags=['disarm'], change=dict(arm=False), type='partition',
        message='{label} special disarming', sub={  # no label passed
            0: dict(type='partition', message='Auto arm cancelled'),
            1: dict(type='partition', message='One-touch stay/instant disarm'),
            2: dict(type='partition', message='Disarming with Winload by {@user}', user=_minor2_provider),
            3: dict(type='partition', tags=['after_alarm'], message='Disarming with Winload after alarm by {@user}',
                    user=_minor2_provider),
            4: dict(type='partition', message='Winload cancelled alarm by {@user}', user=_minor2_provider),
            5: dict(type='partition', message='Future use'),
            6: dict(type='partition', message='Future use'),
            7: dict(type='partition', message='Future use'),
            8: dict(type='partition', message='(InTouch) voice module disarming'),
            9: dict(type='partition', message='Future use')
        }),
    23: dict(
        level=EventLevel.INFO, type='zone', change=dict(bypassed=_toggle_provider), tags=['bypass'],
        message='Zone {label} bypass toggled'),
    24: dict(
        level=EventLevel.CRITICAL, tags=['alarm', 'trigger'], type='zone',
        change=dict(generated_alarm=True, presently_in_alarm=True), message='Zone {label} in alarm',
        hook_fn=_zone_generated_alarm),
    25: dict(
        level=EventLevel.CRITICAL, tags=['alarm', 'fire', 'trigger'], type='zone', change=dict(fire_alarm=True),
        message='Zone {label} in fire alarm', hook_fn=_request_status_refresh),
    26: dict(
        level=EventLevel.WARN, tags=['alarm', 'restore'], type='zone', change=dict(presently_in_alarm=False),
        message='Zone {label} alarm restore', hook_fn=_request_status_refresh),
    27: dict(
        level=EventLevel.WARN, tags=['alarm', 'fire', 'restore'], type='zone', change=dict(fire_alarm=False),
        message='Zone {label} fire alarm restore', hook_fn=_request_status_refresh),
    28: dict(
        level=EventLevel.INFO, type='user', message='{label} Early to disarm by user'),
    29: dict(
        level=EventLevel.INFO, type='user', message='{label} Late to disarm by user'),
    30: dict(
        level=EventLevel.CRITICAL, type='special', message='Special alarm', tags=['alarm', 'trigger'], sub={
            0: dict(message='Panic emergency'),
            1: dict(message='Panic medical'),
            2: dict(message='Panic fire'),
            3: dict(message='Recent closing'),
            4: dict(message='Police code'),
            5: dict(message='Zone shutdown'),
            6: dict(message='Future use 1'),
            7: dict(message='Future use 2'),
            8: dict(message='TLM alarm'),
            9: dict(message='Central communication failure alarm'),
            10: dict(message='Module tamper alarm'),
            11: dict(message='Missing GSM module alarm'),
            12: dict(message='GSM no service alarm'),
            13: dict(message='Missing IP module alarm'),
            14: dict(message='IP no service alarm'),
            15: dict(message='Missing voice module alarm'),
        }, hook_fn=_request_status_refresh),
    31: dict(
        level=EventLevel.CRITICAL, type='user', tags=['alarm', 'trigger'], message='Duress alarm by user {label}',
        hook_fn=_request_status_refresh),
    32: dict(
        level=EventLevel.INFO, type='zone', change=dict(shutdown=True), message='Zone {label} shutdown'),
    33: dict(
        level=EventLevel.INFO, tags=['tamper'], type='zone', change=dict(zone_tamper_trouble=True),
        message='Zone {label} tamper'),
    34: dict(
        level=EventLevel.INFO, tags=['tamper', 'restore'], type='zone', change=dict(zone_tamper_trouble=True),
        message='Zone {label} tamper restore'),
    35: dict(
        level=EventLevel.INFO, tags=['tamper'], type='zone', message='Zone special {label} tamper', sub={
            0: dict(message='Keypad Lockout'),
            1: dict(message='Voice lockout')
        }),
    36: dict(
        level=EventLevel.WARN, type='system', message='Trouble', tags=['trouble'], sub={
            0: dict(message='TLM trouble'),
            1: dict(message='AC failure'),
            2: dict(message='Battery failure'),
            3: dict(message='Auxiliary current overload'),
            4: dict(message='Bell current overload'),
            5: dict(message='Bell disconnected'),
            6: dict(tags=['clock'], message='Clock loss'),
            7: dict(message='Fire loop trouble'),
            8: dict(message='Fail to communicate to monitoring station telephone #1'),
            9: dict(message='Fail to communicate to monitoring station telephone #2'),
            11: dict(message='Fail to communicate to voice report'),
            12: dict(message='RF jamming'),
            13: dict(message='GSM RF jamming'),
            14: dict(message='GSM no service'),
            15: dict(message='GSM supervision lost'),
            16: dict(message='Fail To Communicate IP Receiver 1 (GPRS)'),
            17: dict(message='Fail To Communicate IP Receiver 2 (GPRS)'),
            18: dict(message='IP Module No Service'),
            19: dict(message='IP Module Supervision Loss'),
            20: dict(message='Fail To Communicate IP Receiver 1 (IP)'),
            21: dict(message='Fail To Communicate IP Receiver 2 (IP)')
        }),
    37: dict(
        level=EventLevel.INFO, type='system', message='Trouble restore', tags=['trouble', 'restore'], sub={
            0: dict(message='TLM trouble restore'),
            1: dict(message='AC failure restore'),
            2: dict(message='Battery failure restore'),
            3: dict(message='Auxiliary current overload restore'),
            4: dict(message='Bell current overload restore'),
            5: dict(message='Bell disconnected restore'),
            6: dict(tags=['clock'], message='Clock loss restore'),
            7: dict(message='Fire loop trouble restore'),
            8: dict(message='Fail to communicate to monitoring station telephone #1 restore'),
            9: dict(message='Fail to communicate to monitoring station telephone #2 restore'),
            11: dict(message='Fail to communicate to voice report restore'),
            12: dict(message='RF jamming restore'),
            13: dict(message='GSM RF jamming restore'),
            14: dict(message='GSM no service restore'),
            15: dict(message='GSM supervision lost restore'),
            16: dict(message='Fail To Communicate IP Receiver 1 (GPRS) restore'),
            17: dict(message='Fail To Communicate IP Receiver 2 (GPRS) restore'),
            18: dict(message='IP Module No Service restore'),
            19: dict(message='IP Module Supervision Loss restore'),
            20: dict(message='Fail To Communicate IP Receiver 1 (IP) restore'),
            21: dict(message='Fail To Communicate IP Receiver 2 (IP) restore'),
            99: dict(message='Any trouble event restore')
        }),
    38: dict(
        level=EventLevel.WARN, type='system', message='Module trouble', tags=['trouble'], sub={
            0: dict(message='Combus fault'),
            1: dict(message='Module tamper'),
            2: dict(message='ROM/RAM error'),
            3: dict(message='TLM trouble'),
            4: dict(message='Fail to communicate'),
            5: dict(message='Printer fault'),
            6: dict(message='AC failure'),
            7: dict(message='Battery failure'),
            8: dict(message='Auxiliary failure'),
            9: dict(message='Future use'),
        }, module=_minor2_provider),
    39: dict(
        level=EventLevel.INFO, type='system', message='Module trouble restore', tags=['trouble', 'restore'], sub={
            0: dict(message='Combus fault restored'),
            1: dict(message='Module tamper restored'),
            2: dict(message='ROM/RAM error restored'),
            3: dict(message='TLM trouble restored'),
            4: dict(message='Fail to communicate restored'),
            5: dict(message='Printer fault restored'),
            6: dict(message='AC failure restored'),
            7: dict(message='Battery failure restored'),
            8: dict(message='Auxiliary failure restored'),
            9: dict(message='Future use'),
        }, module=_minor2_provider),
    40: dict(
        level=EventLevel.WARN, type='system', message='Fail to communicate on telephone number',
        telephone=_minor2_provider),
    41: dict(
        level=EventLevel.WARN, type='zone', changes=dict(zone_low_battery_trouble=True), tags=['trouble'],
        message='Low battery on zone {label}'),
    42: dict(
        level=EventLevel.WARN, type='zone', changes=dict(zone_supervision_trouble=True), tags=['trouble'],
        message='Zone {label} supervision trouble'),
    43: dict(
        level=EventLevel.INFO, type='zone', changes=dict(zone_low_battery_trouble=False), tags=['trouble', 'restore'],
        message='Low battery on zone {label} restored'),
    44: dict(
        level=EventLevel.INFO, type='zone', changes=dict(zone_supervision_trouble=False), tags=['trouble', 'restore'],
        message='Zone {label} supervision trouble restored'),
    45: dict(
        level=EventLevel.INFO, type='system', message='Special events', sub={
            0: 'Power-up after total power down',
            1: 'Software reset (watchdog)',
            2: 'Test report',
            3: 'Listen-in request',
            4: 'WinLoad in (connected)',
            5: 'WinLoad out (disconnected)',
            6: 'Installer in programming',
            7: 'Installer out of programming',
            8: 'Future use'
        }),
    46: dict(
        level=EventLevel.WARN, type='user', message='Early to arm by user'),
    47: dict(
        level=EventLevel.WARN, type='user', message='Late to arm by user'),
    48: dict(
        level=EventLevel.INFO, type='utility', message='Utility key'),
    49: dict(
        level=EventLevel.WARN, type='door', message='Request for exit'),
    50: dict(
        level=EventLevel.WARN, type='door', message='Access denied'),
    51: dict(
        level=EventLevel.WARN, type='door', message='Door left open alarm'),
    52: dict(
        level=EventLevel.WARN, type='door', message='Door forced alarm'),
    53: dict(
        level=EventLevel.WARN, type='door', message='Door left open restore'),
    54: dict(
        level=EventLevel.WARN, type='door', message='Door forced open restore'),
    55: dict(
        level=EventLevel.WARN, type='zone', message='Intellizone triggered'),
    56: dict(
        level=EventLevel.WARN, type='zone', message='Zone excluded on Force arming'),
    57: dict(
        level=EventLevel.WARN, type='zone', message='Zone went back to arm status'),
    58: dict(
        level=EventLevel.INFO, type='module', message='New module assigned on combus'),
    59: dict(
        level=EventLevel.INFO, type='module', message='Module manually removed from combus'),
    60: dict(
        level=EventLevel.INFO, type='system', message='Non-saved event', sub={
            0: 'Remote control rejected',
            1: 'Future use'
        }),
    61: dict(
        level=EventLevel.INFO, type='module', message='Module manually removed from combus'),
    62: dict(
        level=EventLevel.INFO, type='user', message='Access granted to user'),
    63: dict(
        level=EventLevel.INFO, type='user', message='Access denied to user'),
    64: dict(
        level=EventLevel.INFO, type='system', message='Status 1', sub={
            0: 'Armed',
            1: 'Force armed',
            2: 'Stay armed',
            3: 'Instant armed',
            4: 'Strobe alarm',
            5: 'Silent alarm',
            6: 'Audible alarm',
            7: 'Fire alarm'
        }),
    65: dict(
        level=EventLevel.INFO, type='system', message='Status 2', sub={
            0: 'Ready',
            1: 'Exit delay',
            2: 'Entry delay',
            3: 'System in trouble',
            4: 'Alarm in memory',
            5: 'Zones bypassed',
            6: 'Bypass, master, installer programming',
            7: 'Keypad lockout'
        }),
    66: dict(
        level=EventLevel.INFO, type='system', message='Status 3', sub={
            0: 'Intellizone delay engaged',
            1: 'Fire delay engaged',
            2: 'Auto arm',
            3: 'Arming with voice module (set until exit delay finishes)',
            4: 'Tamper',
            5: 'Zone low battery',
            6: 'Fire loop trouble',
            7: 'Zone supervision trouble'
        }),
    67: dict(
        level=EventLevel.INFO, type='system', message='Special status', sub={
            # 0-3: Chime in partition 1-4
            4: 'Smoke detector power reset',
            5: 'Ground start',
            6: 'Kiss off',
            7: 'Telephone ring',
            # 8-15: Bell on partition 1-8
            # 16-23: Pulsed alarm in partition
            # 24-31: Open/close Kiss off in partition
            # 32-63: Keyswitch/PGM input
            # 64-95: Status of access door
            96: 'Trouble in system',
            97: 'Trouble in dialer',
            98: 'Trouble in module',
            99: 'Trouble in combus',
            103: 'Time and date trouble',
            104: 'AC failure',
            105: 'Battery failure',
            106: 'Auxiliary current limit',
            107: 'Bell current limit',
            108: 'Bell absent',
            109: 'ROM error',
            110: 'RAM error',
            111: 'Future use',
            112: 'TLM 1 trouble',
            113: 'Fail to communicate 1',
            114: 'Fail to communicate 2',
            115: 'Fail to communicate 3',
            116: 'Fail to communicate 4',
            117: 'Fail to communicate with PC',
            120: 'Module tamper trouble',
            121: 'Module ROM error',
            122: 'Module TLM error',
            123: 'Module Failure to communicate',
            124: 'Module printer trouble',
            125: 'Module AC failure',
            126: 'Module battery trouble',
            127: 'Module auxiliary failure',
            128: 'Missing  keypad',
            129: 'Missing  module',
            133: 'Global combus failure',
            134: 'Combus overload',
            136: 'Dialer relay',
        }),
}
