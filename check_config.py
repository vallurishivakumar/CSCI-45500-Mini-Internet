import json

with open("config/topology.json", "r") as file:
    config = json.load(file)

print("Configuration loaded successfully.")
print("Nodes:")

for name, node in config["nodes"].items():
    print(name, "->", node["ip"], node["port"])