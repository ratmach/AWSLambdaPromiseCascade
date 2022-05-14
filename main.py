from utils import SharedMemory
import json

shared_memory = SharedMemory()
shared_memory.some_variable = "value"
shared_memory["some_value"] = json.dumps({"something": "that is", "json": "encodable"})

other_shared_memory = SharedMemory(shared_memory.uid)
print(other_shared_memory.some_variable)
print(json.loads(other_shared_memory["some_value"].decode("utf-8")))
