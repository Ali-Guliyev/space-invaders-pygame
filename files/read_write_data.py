import json

def update_file(src, key, storing_data):
  data = ""
  with open(src, "r") as f:
    data = json.load(f)
    data[key] = storing_data

  with open(src, "w") as f:
    json.dump(data, f)

def read_file(src, key):
  with open(src, "r") as f:
    return json.load(f)[key]