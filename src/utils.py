with open('constants.txt') as f:
    lines = f.readlines()
    global_dict = {}
    for line in lines:
        key, val = line.split('=')
        key = key.strip()
        val = val.strip()
        global_dict[key] = val

def get_global(key):
    return global_dict[key]