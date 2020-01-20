
def history_dict_to_json(run, payload, step=None):
    # Converts a History row dict's elements so they're friendly for JSON serialization.

    if step is None:
        # We should be at the top level of the History row; assume this key is set.
        step = payload['_step']

    # We use list here because we were still seeing cases of RuntimeError dict changed size
    for key in list(payload):
        val = payload[key]
        if isinstance(val, dict):
            payload[key] = history_dict_to_json(run, val, step=step)
        else:
            payload[key] = val_to_json(run, key, val, step=step)

    return payload