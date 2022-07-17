def logger(*args, **kwargs):
    if kwargs:
        print(*args, kwargs, flush=True)
    else:
        print(*args, flush=True)


def remove_special_chars_in_string(string: str, variables: list[str] = ["$", "^", "{", "}"]):
    for var in variables:
        string = string.replace(var, "")
    return string
