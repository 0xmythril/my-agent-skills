#!/usr/bin/env python3
"""Emit a valid ffmpeg filtergraph that redacts regions of a screen recording.

Handles the mechanical constraints that break hand-written redaction filtergraphs:
boxblur radius limits (which are set by the *chroma* plane, not the region), empty
filter segments from trailing separators, and odd output dimensions.

    build_filtergraph.py IN.mov --region 1130,450,420,530@6.5-10.5 -o graph.txt

Region syntax: x,y,w,h            (whole clip)
               x,y,w,h@start-end  (seconds, inclusive)
"""

import argparse
import json
import re
import subprocess
import sys

REGION_RE = re.compile(
    r"^(?P<x>\d+),(?P<y>\d+),(?P<w>\d+),(?P<h>\d+)"
    r"(?:@(?P<start>\d+(?:\.\d+)?)-(?P<end>\d+(?:\.\d+)?))?$"
)


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "json", path],
        capture_output=True, text=True, check=True,
    )
    s = json.loads(out.stdout)["streams"][0]
    return s["width"], s["height"]


def chroma_divisor(pix_fmt):
    """Chroma planes are subsampled, and boxblur's radius limit is per-plane.

    This must reflect the pixel format the filter chain actually runs in, which is
    the *encode* target rather than the source: ffmpeg negotiates the graph down to
    yuv420p for an h264 output even when the input is RGB, and boxblur is then
    validated against the subsampled chroma plane.
    """
    if "420" in pix_fmt:
        return 2, 2
    if "422" in pix_fmt:
        return 2, 1
    return 1, 1  # 444 / rgb: chroma is full resolution


def blur_filter(w, h, pix_fmt, strength):
    """boxblur radii clamped so both the luma and chroma planes stay legal.

    ffmpeg rejects radius > min(plane_w, plane_h) / 2, and when the 4-param form is
    omitted the chroma radius inherits the luma value and blows the tighter limit.
    """
    cw, ch = chroma_divisor(pix_fmt)
    luma_max = min(w, h) // 2
    chroma_max = min(w // cw, h // ch) // 2
    luma = max(1, min(strength, luma_max))
    chroma = max(1, min(strength, chroma_max))
    return f"boxblur={luma}:2:{chroma}:2"


def pixelate_filter(w, h, _pix_fmt, strength):
    """Scale down then back up with nearest-neighbour. Legal at any region size."""
    factor = max(2, min(strength, min(w, h)))
    dw, dh = max(1, w // factor), max(1, h // factor)
    return f"scale={dw}:{dh},scale={w}:{h}:flags=neighbor"


MODES = {"blur": blur_filter, "pixelate": pixelate_filter}


def parse_region(spec):
    m = REGION_RE.match(spec.strip())
    if not m:
        sys.exit(f"error: bad region {spec!r} (want x,y,w,h or x,y,w,h@start-end)")
    g = m.groupdict()
    r = {k: int(g[k]) for k in ("x", "y", "w", "h")}
    if r["w"] < 2 or r["h"] < 2:
        sys.exit(f"error: region {spec!r} is too small to redact")
    r["start"] = float(g["start"]) if g["start"] else None
    r["end"] = float(g["end"]) if g["end"] else None
    return r


def build(regions, vid_w, vid_h, pix_fmt, mode, strength):
    make = MODES[mode]
    parts, cur = [], "0:v"
    for i, r in enumerate(regions, 1):
        if r["x"] + r["w"] > vid_w or r["y"] + r["h"] > vid_h:
            sys.exit(f"error: region {i} ({r['x']},{r['y']},{r['w']},{r['h']}) "
                     f"falls outside the {vid_w}x{vid_h} frame")
        keep, cut = f"m{i}", f"s{i}"
        parts.append(f"[{cur}]split=2[{keep}][{cut}]")
        parts.append(
            f"[{cut}]crop={r['w']}:{r['h']}:{r['x']}:{r['y']},"
            f"{make(r['w'], r['h'], pix_fmt, strength)}[b{i}]"
        )
        overlay = f"overlay={r['x']}:{r['y']}"
        if r["start"] is not None:
            overlay += f":enable='between(t,{r['start']},{r['end']})'"
        cur = f"v{i}"
        parts.append(f"[{keep}][b{i}]{overlay}[{cur}]")

    # libx264 refuses odd dimensions; trunc is a no-op when they are already even.
    parts.append(f"[{cur}]scale=trunc(iw/2)*2:trunc(ih/2)*2[vout]")

    graph = ";".join(p for p in parts if p)
    assert ";;" not in graph and ",," not in graph, "empty filter segment"
    return graph


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("input")
    ap.add_argument("--region", action="append", required=True,
                    help="x,y,w,h or x,y,w,h@start-end (repeatable)")
    ap.add_argument("--mode", choices=sorted(MODES), default="pixelate")
    ap.add_argument("--target-pix-fmt", default="yuv420p",
                    help="pixel format the encode targets; sets the boxblur chroma "
                         "radius limit (default: yuv420p)")
    ap.add_argument("--strength", type=int, default=12,
                    help="blur radius, or pixelate block divisor (default: 12)")
    ap.add_argument("-o", "--output", help="write graph here (default: stdout)")
    args = ap.parse_args()

    vid_w, vid_h = probe(args.input)
    regions = [parse_region(s) for s in args.region]
    graph = build(regions, vid_w, vid_h, args.target_pix_fmt, args.mode, args.strength)

    if args.output:
        with open(args.output, "w") as fh:
            fh.write(graph)
        print(f"{args.output}: {len(regions)} region(s), {vid_w}x{vid_h} "
              f"-> {args.target_pix_fmt}, mode={args.mode}", file=sys.stderr)
    else:
        print(graph)


if __name__ == "__main__":
    main()
