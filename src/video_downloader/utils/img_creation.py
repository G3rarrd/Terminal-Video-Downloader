import io
import PIL.Image as PILImage
import PIL.ImageDraw as PILImageDraw

def create_broken_image_placeholder(
    width: int = 640,
    height: int = 360,
    bg_color: tuple[int, int, int] = (30, 30, 30),
    icon_color: tuple[int, int, int] = (140, 140, 140),
) -> PILImage.Image:
    """Generates a placeholder image featuring a drawn broken-image icon."""
    img = PILImage.new("RGB", (width, height), bg_color)
    draw = PILImageDraw.Draw(img)

    # Calculate center bounding box for picture frame icon (40x30 approx)
    cx, cy = width // 2, height // 2
    fw, fh = 20, 15  # Half-widths for frame

    frame_box = [cx - fw, cy - fh, cx + fw, cy + fh]

    # 1. Outer Frame
    draw.rectangle(frame_box, outline=icon_color, width=2)

    # 2. Mountain/Hill geometry inside frame
    m_left = [cx - fw + 3, cy + fh - 2]
    m_peak = [cx - 5, cy - 2]
    m_right = [cx + 8, cy + fh - 2]
    draw.polygon([m_left[0], m_left[1], m_peak[0], m_peak[1], m_right[0], m_right[1]], outline=icon_color)

    # 3. Sun/Circle in upper-right corner of frame
    sun_box = [cx + 5, cy - fh + 4, cx + 12, cy - fh + 11]
    draw.ellipse(sun_box, outline=icon_color)

    # 4. Diagonal "Broken" Crack / Strike-through line across icon
    draw.line([cx - fw - 4, cy - fh - 4, cx + fw + 4, cy + fh + 4], fill=(200, 60, 60), width=2)

    return img