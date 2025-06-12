# utils/debug.py
from pprint import pprint
import json


def print_r(value, json_mode=False):
    if json_mode:

        def convert(obj):
            if hasattr(obj, "__dict__"):
                return obj.__dict__
            return obj

        print(json.dumps(value, default=convert, indent=4))
    else:
        from pprint import pprint

        if hasattr(value, "__dict__"):
            pprint(value.__dict__)
        elif isinstance(value, list):
            pprint([v.__dict__ if hasattr(v, "__dict__") else v for v in value])
        else:
            pprint(value)
