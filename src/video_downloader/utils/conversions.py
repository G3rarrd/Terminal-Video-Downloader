def convert_duration(duration: int) -> str:
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = [hours, minutes, seconds]
    while len(parts) > 1 and parts[0] == 0:
        parts.pop(0)

    return ":".join(f"{p:02d}" for p in parts)