import typing, inspect, re, json, yaml, datetime, base64, os


class ObjectEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.date):
            return obj.isoformat()
        elif hasattr(obj, "to_dict"):
            return self.default(obj.to_dict())
        elif hasattr(obj, "__dict__"):
            d = dict(
                (key, value)
                for key, value in inspect.getmembers(obj)
                if not key.startswith("__")
                and not inspect.isabstract(value)
                and not inspect.isbuiltin(value)
                and not inspect.isfunction(value)
                and not inspect.isgenerator(value)
                and not inspect.isgeneratorfunction(value)
                and not inspect.ismethod(value)
                and not inspect.ismethoddescriptor(value)
                and not inspect.isroutine(value)
            )
            return self.default(d)
        return obj


def log_error(e: Exception, retry: bool = False):
    print(f"Error: {e}")
    if retry:
        print("Retrying...")


async def try_loop_async(func: typing.Callable, max_retries: int = 3):
    exception = Exception()
    for num_retry in range(max_retries, -1, -1):
        try:
            return await func()
        except Exception as e:
            exception = e
            log_error(e, retry=num_retry > 0)
    raise exception


def try_loop(func: typing.Callable, max_retries: int = 3):
    exception = Exception()
    for num_retry in range(max_retries, -1, -1):
        try:
            return func()
        except Exception as e:
            exception = e
            log_error(e, retry=num_retry > 0)
    raise exception


def dump_json(data: typing.Any, **kwargs) -> str:
    return json.dumps(data, cls=ObjectEncoder, ensure_ascii=False, indent=4, **kwargs)


def dump_yaml(data: typing.Any, **kwargs) -> str:
    return yaml.dump(data, allow_unicode=True, **kwargs)


def extract_code_blocks(
    text: str, target_cls: str | None = None
) -> list[tuple[str, str]]:
    matches = re.findall(r"```(.*?)\n(.*?)\n```", text, re.DOTALL)
    code_blocks = [
        (str(cls), str(code).strip()) for cls, code in matches if cls == target_cls
    ]
    return code_blocks


def extract_json(text: str) -> tuple[str, typing.Any]:
    json_codes = [code for _, code in extract_code_blocks(text, target_cls="json")]

    if len(json_codes or []) != 1:
        raise ValueError("Expected exactly one JSON code block in the text")

    json_code = str(json_codes[0]).strip()
    data = json.loads(json_code)
    return json_code, data


def extract_yaml(text: str) -> tuple[str, typing.Any]:
    yaml_codes = [code for _, code in extract_code_blocks(text, target_cls="yaml")]

    if len(yaml_codes or []) != 1:
        raise ValueError("Expected exactly one YAML code block in the text")

    yaml_code = str(yaml_codes[0]).strip()
    data = yaml.safe_load(yaml_code)

    return yaml_code, data


def verify_data(data: typing.Any, schema: type | dict | list | typing.Any) -> bool:
    if isinstance(schema, type):
        return isinstance(data, schema)
    if type(data) != type(schema):
        return False
    if isinstance(schema, dict):
        for key, value in schema.items():
            if key not in data:
                return False
            if not verify_data(data[key], value):
                return False
    elif isinstance(schema, list):
        if len(data) != len(schema):
            return False
        for d, p in zip(data, schema):
            if not verify_data(d, p):
                return False
    else:
        if data != schema:
            return False
    return True


def encode_image_to_base64_data_uri(file_path):
    # Determine the MIME type based on the file extension
    mime_type = None
    extension = os.path.splitext(file_path)[1].lower()

    if extension in [".jpg", ".jpeg"]:
        mime_type = "image/jpeg"
    elif extension == ".png":
        mime_type = "image/png"
    elif extension == ".gif":
        mime_type = "image/gif"
    else:
        raise ValueError("Unsupported file extension")

    # Open the image file in binary mode
    with open(file_path, "rb") as image_file:
        # Read the file content
        image_data = image_file.read()
        # Encode the binary data to base64
        encoded_image = base64.b64encode(image_data)
        # Convert the encoded bytes to a string
        encoded_string = encoded_image.decode("utf-8")

    # Format as a data URI
    data_uri = f"data:{mime_type};base64,{encoded_string}"
    return data_uri
