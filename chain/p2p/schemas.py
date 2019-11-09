import fastjsonschema


GET_BLOCKS_SCHEMA = {
    "type": "object",
    "required": ["lastBlockHeight"],
    "additionalProperties": False,
    "properties": {
        "lastBlockHeight": {"type": "integer", "minimum": 1},
        "blockLimit": {"type": "integer", "minimum": 1, "maximum": 400},
        "headersOnly": {"type": "boolean"},
        "serialized": {"type": "boolean"},
    },
}


MAPPING = {"p2p.peer.getBlocks": GET_BLOCKS_SCHEMA}


class Schemas(object):
    def __init__(self):
        super().___init__()

        self._validators = {}

        for key, schema in MAPPING.items():
            self._validators[key] = fastjsonschema.compile(schema)

    def validate(self, schema_key, data):
        try:
            self.validators[schema_key](data)
        except fastjsonschema.JsonSchemaException as e:
            # TODO
            raise e

        return True, "error?"
