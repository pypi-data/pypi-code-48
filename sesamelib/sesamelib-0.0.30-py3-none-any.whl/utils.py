import os


def lookup_env(name, default=None):
    """Get a value from the env if it exists.

    Fallback to default if the environment variable isn't found. This is
    mainly used in cli parsing arguments to comply (a bit) with 12-factors
    apps.

    Args:
        name (str): variable name to look for
        default: default value
    """
    return os.environ.get(name, default)


def lookup_env_array(name, default=None):
    """Get an array from the env if it exists.

    The array is serialized as a coma-separated string in the env.
    """

    lookup = lookup_env(name, default=default)
    if not lookup:
        return []
    else:
        return lookup.split(",")


def lookup_env_int(name, default=None):
    """Get an int from the env if it exists."""
    lookup = lookup_env(name, default=default)
    return int(lookup)

