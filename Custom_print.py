# Custom_print.py
import inspect
import hashlib
import builtins

def get_color_from_hash(text):
    # 텍스트로부터 해시 생성
    hash_object = hashlib.md5(text.encode())
    hash_hex = hash_object.hexdigest()

    # 해시값을 RGB 색상으로 변환
    r = int(hash_hex[:2], 16)
    g = int(hash_hex[2:4], 16)
    b = int(hash_hex[4:6], 16)

    # 밝은 계열 색상으로 조정 (RGB 값이 일정 이상이도록)
    r = 128 + r // 2  # 128 ~ 255 범위로 조정
    g = 128 + g // 2
    b = 128 + b // 2

    return r, g, b

def colored_text(text, color_code):
    return f"\033[38;2;{color_code[0]};{color_code[1]};{color_code[2]}m{text}\033[0m"

def custom_print(*args, **kwargs):
    frame = inspect.currentframe().f_back
    info = inspect.getframeinfo(frame)

    # Get the class name if it exists
    class_name = ''
    if 'self' in frame.f_locals:
        class_name = frame.f_locals['self'].__class__.__name__ + '.'

    # Generate color based on class name and line number
    color_seed = f"{class_name}{info.function}:{info.lineno}"
    color_code = get_color_from_hash(color_seed)

    # Color all arguments with the same color
    colored_args = [colored_text(f"{arg}", color_code) for arg in args]

    # Use the original print function from builtins
    builtins._original_print(f' ==> {class_name}{info.function}: Line {info.lineno}:', *colored_args, **kwargs)

# Save the original print function
builtins._original_print = builtins.print
# Override the built-in print function
builtins.print = custom_print