import re

INI_ID_RE = re.compile(r"^(\d+)\|")


def analyze_ini_file(file_path: str, pipe_count: int) -> dict:
    last_valid_id = None
    current_id = None
    buffer = []
    is_broken = False
    error_message = ""

    def validate_record():
        nonlocal last_valid_id, current_id, buffer

        if current_id is None:
            return True

        text = "".join(buffer)
        if text.count("|") != pipe_count:
            return False

        last_valid_id = current_id
        return True

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            for line in file:
                match = INI_ID_RE.match(line)

                if match:
                    if not validate_record():
                        is_broken = True
                        break

                    current_id = int(match.group(1))
                    buffer = [line]
                else:
                    if current_id is not None:
                        buffer.append(line)

        if not is_broken and current_id is not None:
            if "".join(buffer).count("|") == pipe_count:
                last_valid_id = current_id
            else:
                is_broken = True

        return {
            "last_valid_id": last_valid_id,
            "is_broken": is_broken,
            "error_message": error_message,
        }

    except Exception as error:
        return {
            "last_valid_id": last_valid_id,
            "is_broken": True,
            "error_message": str(error),
        }