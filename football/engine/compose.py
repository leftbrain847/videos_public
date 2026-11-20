"""Final 1080x1920 short: story on top, Disk Football on the bottom, af_heart narration.

python3 compose.py <video_dir> --out <file.mp4>
"""
import argparse, subprocess
from pathlib import Path

ROOT = Path(__file__).parent
LAYOUT = {
    "size": [1080, 1920], "seconds": 60.0,
    "divider": {"h": 8, "color": "0x111111"},
    "pill": {"text": "DISK FOOTBALL", "x": 36, "y": 1846, "size": 34, "color": "white", "box": "0x111111@0.72", "pad": 16},
    "crf": 23, "preset": "veryfast", "audio_kbps": 128,
}


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("video_dir"); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    b = Path(a.video_dir) / "build"; L = LAYOUT; pl = L["pill"]; d = L["divider"]
    font = ROOT / "fonts" / "Inter-Black.otf"
    vf = (f"[0:v][1:v]vstack=inputs=2[v];"
          f"[v]drawbox=x=0:y={L['size'][1] // 2 - d['h'] // 2}:w={L['size'][0]}:h={d['h']}:color={d['color']}:t=fill,"
          f"drawtext=fontfile='{font}':text='{pl['text']}':x={pl['x']}:y={pl['y']}:fontsize={pl['size']}:fontcolor={pl['color']}:box=1:boxcolor={pl['box']}:boxborderw={pl['pad']}[out]")
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(b / "top.mp4"), "-i", str(b / "bottom.mp4"), "-i", str(b / "mix.wav" if (b / "mix.wav").exists() else b / "narration.wav"),
                    "-filter_complex", vf, "-map", "[out]", "-map", "2:a", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-t", str(L["seconds"]),
                    "-c:v", "libx264", "-preset", L["preset"], "-crf", str(L["crf"]), "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-b:a", f"{L['audio_kbps']}k", "-movflags", "+faststart", a.out], check=True)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
