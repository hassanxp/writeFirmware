import yaml

dict = {0xa0: {"address": 0xffff, "file": "abc/xyz-0xa0.bin"},
        0xb1: {"address": 0xace0, "file": "abc/xyz-0xb1.bin"}}

print(dict)

with open("document.yaml", 'w') as f:
    yaml.dump(dict, f)


with open("config.yaml", 'r') as f:
    data = yaml.safe_load(f)
    print(data)
