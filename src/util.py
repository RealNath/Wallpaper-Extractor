import winreg as wrg
import re

def get_current_wallpaper_path():
    '''
    Obtain the file directory of the current wallpaper image
    '''
    with wrg.OpenKey(wrg.HKEY_CURRENT_USER,
                    r"Control Panel\Desktop",
                    0, wrg.KEY_READ | wrg.KEY_WOW64_64KEY) as desktop:
        val, _ = wrg.QueryValueEx(desktop, "TranscodedImageCache")

    val_utf16 = val.decode("utf-16", errors="ignore")

    match = re.search(r"[A-Z]:\\[^\0]+", val_utf16)
    if match: return (match.group(0))
    else: return ("Wallpaper path not found.")