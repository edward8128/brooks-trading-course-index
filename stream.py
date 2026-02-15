import os
import sys
import platform
import shutil
import subprocess


#install vlc and streamlink (and python)
#go to course video, F12 (developer tool) > Network> search for a url ending in... playlist.m3u8
#than run >>python stream.py "https:/..... playlist.m3u8"

ORIGIN  = "https://iframe.mediadelivery.net"
REFERER = "https://iframe.mediadelivery.net/"
QUALITY = "best"

def default_ua() -> str:
    # Good-enough Chrome UA per platform (doesn't need to be exact)
    system = platform.system().lower()
    if "windows" in system:
        return ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    if "darwin" in system:  # macOS
        return ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    # Linux
    return ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")

def find_vlc() -> str | None:
    # Prefer PATH
    vlc = shutil.which("vlc")
    if vlc:
        return vlc

    system = platform.system().lower()

    # Common Windows paths
    if "windows" in system:
        candidates = [
            r"C:\Program Files\VideoLAN\VLC\vlc.exe",
            r"C:\Program Files (x86)\VideoLAN\VLC\vlc.exe",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p

    # macOS app bundle
    if "darwin" in system:
        p = "/Applications/VLC.app/Contents/MacOS/VLC"
        if os.path.exists(p):
            return p

    # Linux common
    for name in ("vlc", "cvlc"):
        p = shutil.which(name)
        if p:
            return p

    return None

def streamlink_available() -> bool:
    # Don't rely on PATH; check python -m streamlink
    try:
        p = subprocess.run([sys.executable, "-m", "streamlink", "--version"],
                           capture_output=True, text=True)
        return p.returncode == 0
    except Exception:
        return False
def find_streamlink() -> str | None:
    # Prefer PATH first
    exe = shutil.which("streamlink")
    if exe:
        return exe

    system = platform.system().lower()

    if "windows" in system:
        candidates = [
            r"C:\Program Files\Streamlink\bin\streamlink.exe",
            r"C:\Program Files (x86)\Streamlink\bin\streamlink.exe",
        ]
        for p in candidates:
            if os.path.exists(p):
                return p

    if "darwin" in system:
        exe = shutil.which("streamlink")
        if exe:
            return exe

    if "linux" in system:
        exe = shutil.which("streamlink")
        if exe:
            return exe

    return None

def main():
    if len(sys.argv) < 2:
        print("Usage: python play_hls.py <M3U8_URL>")
        sys.exit(2)

    url = sys.argv[1].strip()

    streamlink = find_streamlink()
    if not streamlink:
        print("Error: streamlink was not found.")
        print("Install Streamlink from:")
        print("https://streamlink.github.io/install.html")
        sys.exit(1)

    vlc = find_vlc()
    if not vlc:
        print("Error: VLC was not found.")
        print("Install VLC, or ensure 'vlc' is on PATH.")
        sys.exit(1)

    ua = os.environ.get("HLS_UA", default_ua())  # allow override via env var

    cmd = [
        streamlink,
        "--http-header", f"origin={ORIGIN}",
        "--http-header", f"referer={REFERER}",
        "--http-header", f"user-agent={ua}",
        "--retry-open", "3",
        "--retry-streams", "3",
        "--player", vlc,
        "--player-args", "--network-caching=1500",
        url,
        QUALITY
    ]

    print("Running:", " ".join(cmd))
    subprocess.run(cmd, check=False)

if __name__ == "__main__":
    main()
