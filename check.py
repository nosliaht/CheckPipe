import re

INI_ID_RE = re.compile(r"^(\d+)\|")


def get_last_valid_id(file_path: str, pipe_count: int):
    last_valid_id = None
    current_id = None
    buffer = []

    def close_record():
        nonlocal last_valid_id, current_id, buffer

        if current_id is None:
            return True

        text = "".join(buffer)
        if text.count("|") != pipe_count:
            return False

        last_valid_id = current_id
        return True

    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            match = INI_ID_RE.match(line)

            if match:
                if not close_record():
                    return last_valid_id

                current_id = int(match.group(1))
                buffer = [line]
            else:
                if current_id is not None:
                    buffer.append(line)

    if current_id is not None and "".join(buffer).count("|") == pipe_count:
        last_valid_id = current_id

    return last_valid_id