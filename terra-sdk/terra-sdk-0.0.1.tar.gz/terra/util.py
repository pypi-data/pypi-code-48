import json

class JsonSerializable:
    def to_json(self, sort: bool = False) -> str:
        """Return the `json.dumps` of the current object.
        If one of the attributes in `__dict__` is not serializable to json,
        assume it's an object and gather its attributes via `__dict__`.
        """
        return json.dumps(
            self.__dict__,
            sort_keys=sort,
            separators=(",", ":"),
            default=lambda o: o.__dict__,
        )