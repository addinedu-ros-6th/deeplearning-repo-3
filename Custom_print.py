import inspect
import random

def print(*args, **kwargs):
    frame = inspect.stack()[1]
    filename = frame.filename
    lineno = frame.lineno
    funcname = frame.function
    classname = frame.frame.f_locals["self"].__class__.__name__ if "self" in frame.frame.f_locals else None

    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
    }
    color = random.choice(list(colors.values()))

    for arg in args:
        if isinstance(arg, str):
            var_name = arg
            var_value = arg
        else:
            var_name = [k for k, v in frame.frame.f_locals.items() if v is arg]
            var_name = var_name[0] if var_name else "Unknown"
            var_value = arg

        print_string = f"{color}{classname + '.' if classname else ''}{funcname} ({filename}:{lineno}) - {var_name}: {var_value}\033[0m"
        __builtins__.print(print_string, **kwargs)