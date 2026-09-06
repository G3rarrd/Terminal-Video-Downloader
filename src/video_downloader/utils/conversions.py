def convert_duration(duration: int) -> str:
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = [hours, minutes, seconds]
    while len(parts) > 1 and parts[0] == 0:
        parts.pop(0)

    return ":".join(f"{p:02d}" for p in parts)

def convert_eta(duration: float) -> str:
    duration = int(duration)
    
    hours, remainder = divmod(duration, 3600)
    minutes, seconds = divmod(remainder, 60)

    var_names = [hours, minutes, seconds]
    t = ["hours", "minutes", "seconds"]
    while len(var_names) > 1 and var_names[0] == 0:
        var_names.pop(0)
        t.pop(0)

    return " ".join(f"{p} {t[i]}" for i, p in enumerate(var_names))