def format_bytes(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


def format_speed(speed: float | None) -> str:
    if not speed:
        return "—"
    return f"{format_bytes(int(speed))}/s"


def render_bar(pct: float, width: int = 16) -> str:
    filled = int(width * pct / 100)
    return "█" * filled + "░" * (width - filled)

