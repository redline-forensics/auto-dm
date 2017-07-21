import os

_curr_dir = os.path.dirname(os.path.realpath(__file__))
resources = {}


def get_resources_dicts(path):
    path = os.path.normpath(path).split(os.sep)
    _curr_dir_index = path.index(os.path.basename(_curr_dir)) + 1
    if _curr_dir_index >= len(path):
        path = []
    else:
        path = path[_curr_dir_index:]
    return "".join("[\"{}\"]".format(folder) for folder in path)


for dir_name, dir_names, file_names in os.walk(_curr_dir):
    try:
        file_names.remove(os.path.basename(__file__))
    except ValueError:
        pass

    resources_dicts = get_resources_dicts(dir_name)

    # print("### dir_names ###")
    for sub_dir_name in dir_names:
        # print("{} - {}".format(dir_name, sub_dir_name))
        exec ("resources{dicts}[\"{curr_dir}\"] = {{}}".format(dicts=resources_dicts, curr_dir=sub_dir_name))

    # print("### file_names ###")
    for file_name in file_names:
        # print("{} - {}".format(dir_name, file_name))
        # print(os.path.join(dir_name, file_name))
        exec ("resources{dicts}[\"{curr_file}\"] = \"{file_path}\"".format(dicts=resources_dicts, curr_file=file_name,
                                                                           file_path=os.path.join(dir_name,
                                                                                                  file_name).replace(
                                                                               "\\", "/")))
