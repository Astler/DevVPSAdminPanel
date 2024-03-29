import os


def open_internal_file(path_to_file: str, open_mode: str = "a+", encoding='utf-8'):
    if path_to_file.__contains__("/"):
        path = "".join(path_to_file.split("/")[:-1])
        os.makedirs(path, exist_ok=True)

    if not os.path.exists(path_to_file):
        return open(path_to_file, "a+", encoding=encoding)

    return open(path_to_file, open_mode, encoding=encoding)
