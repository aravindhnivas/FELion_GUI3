def logger(*args, **kwargs):
    if kwargs:
        print(args, kwargs, flush=True)
    else:
        print(args, flush=True)
