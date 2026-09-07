---
name: redact-demo-recording
version: 1.0.0
description: >-
  Use when a screen recording or demo video needs personal or sensitive content
  removed before it is shared — blurring email addresses, faces, wallet addresses,
  API keys or account details, stripping audio, cutting or fast-forwarding a login
  segment, or converting the result to mp4. Triggers on requests like "blur my email
  out of this video", "remove the audio", "fast forward through the login", or a
  .mov/.mp4 handed over for cleanup before a demo or public post.
metadata:
  hermes:
    tags: [video, ffmpeg, redaction, privacy, screen-recording, demo]
    category: media
    requires_toolsets: [terminal]
---

# Redact a demo recording

Remove sensitive content from a screen recording without destroying the demo it is
meant to show. The output gets shared externally, so an incomplete redaction is the
failure mode that matters — a slightly ugly blur is fine, a leaked email is not.

## Workflow

### 1. Probe before anything else

```bash
ffprobe -v error -show_entries stream=width,height,r_frame_rate,codec_type,duration \
  -of default=noprint_wrappers=1 IN.mov
```

Note the dimensions and whether an audio stream exists. Screen recordings from Retina
displays are routinely odd-sized (e.g. `2940x1833`), which libx264 rejects outright.

### 2. Find the regions by looking, never by guessing

This is the step that decides whether the job takes three commands or three hundred.
Extract frames at the timestamps where the sensitive content is visible and **view the
PNGs** to read off coordinates:

```bash
for t in 6 10 21 36; do
  ffmpeg -v error -y -ss $t -i IN.mov -frames:v 1 frame_$t.png
done
```

Read each frame with the image-reading tool and measure the region in **source pixels**.
If a frame was downscaled for display, multiply the coordinates back up by the stated
factor before using them.

Ask the user which content must go if it is ambiguous — an over-blurred demo is a
wasted re-render, an under-blurred one is a leak.

### 3. Generate the filtergraph

`build_filtergraph.py` handles the constraints that break hand-written graphs (see
Common mistakes). Regions are `x,y,w,h` or `x,y,w,h@start-end` in seconds:

```bash
./build_filtergraph.py IN.mov \
  --region 1130,450,420,530@6.5-10.5 \
  --region 240,552,550,90@9.9-13.5 \
  --mode blur --strength 20 -o graph.txt
```

`--mode pixelate` (the default) is legal at any region size; `--mode blur` is softer
but its radius gets clamped on small regions. Run with `--help` for all options.

Omit the `@start-end` window when the content is on screen for the whole clip. Prefer a
window when it is not — a permanent blur over a region the demo needs later is the most
common re-render cause.

### 4. Verify on single frames before encoding the whole file

A full encode of a multi-minute 4K recording is slow. Check the graph on stills first:

```bash
for t in 7 10 22 36; do
  ffmpeg -v error -y -ss $t -i IN.mov -filter_complex_script graph.txt \
    -map "[vout]" -frames:v 1 check_$t.png
done
```

View them. Only proceed when every region lands where intended.

### 5. Encode

```bash
ffmpeg -y -loglevel error -stats -i IN.mov \
  -filter_complex_script graph.txt -map "[vout]" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -movflags +faststart -an \
  "OUT.mp4"
```

`-an` drops audio. Keep it unless the user wants sound — demo recordings frequently
capture background conversation. To keep audio, replace `-an` with `-c:a aac -b:a 128k`.

### 6. Verify the output, then report

Re-extract frames **from the finished file** at the sensitive timestamps and view them.
Confirm the content is unreadable. State plainly what was redacted and what was left.

## Cutting and speeding up segments

Trim a section (fast, no re-encode of the filter chain):

```bash
ffmpeg -y -v error -ss 0 -to 12 -i IN.mov -c copy part1.mp4
```

Speed a segment up 8x — `setpts` for video, and drop `-an` only if keeping audio:

```bash
ffmpeg -y -v error -i part2.mp4 -vf "setpts=PTS/8" -an part2_fast.mp4
```

Then concatenate parts that share codec and dimensions:

```bash
printf "file '%s'\n" part1.mp4 part2_fast.mp4 part3.mp4 > parts.txt
ffmpeg -y -v error -f concat -safe 0 -i parts.txt -c copy OUT.mp4
```

## Quick reference

| Need | Approach |
| --- | --- |
| Blur a fixed region | `--region x,y,w,h` |
| Blur only while visible | `--region x,y,w,h@start-end` |
| Region too small for blur | `--mode pixelate` (works at any size) |
| Strip audio | `-an` |
| Odd source dimensions | handled automatically by the generated graph |
| Fast-forward a segment | `setpts=PTS/N` on a split-out part, then concat |
| Burn in a text label | not available — this ffmpeg build has no `drawtext` |

## Common mistakes

- **Guessing coordinates instead of extracting a frame.** The dominant cause of
  repeated re-renders. Always measure from a real frame.
- **Encoding the full file to check a blur.** Check stills first (step 4).
- **`boxblur` radius too large for the region.** ffmpeg validates the radius against
  the *chroma* plane, which is half-size in yuv420p — a 28px-tall region allows a
  chroma radius of only 7. Omitting the 4-parameter form makes chroma inherit the luma
  radius and fail. The generator clamps both; do not hand-edit radii back up.
- **Odd width or height.** `height not divisible by 2` kills the encode. The generated
  graph ends in `scale=trunc(iw/2)*2:trunc(ih/2)*2` to prevent it.
- **Assembling a filtergraph in a shell loop.** Quoting and `$`-expansion silently
  corrupt filter names (`flags=` became `26ags`, `enable=` became `nable` in past runs).
  Write the graph to a file and use `-filter_complex_script`.
- **Empty filter segments.** A trailing `,` or a doubled `;` yields
  `No such filter: ''`. The generator never emits them.
- **Declaring the job done without viewing the output.** The deliverable is a file the
  user will publish. Look at it first.

## Regression tests

`test_build_filtergraph.py` covers the failure modes the generator exists to prevent
(chroma-clamped `boxblur`, odd source dimensions, out-of-bounds regions, empty filter
segments, both modes, time windows, multi-region chaining). It stubs nothing but also
never calls `ffprobe`, so it runs anywhere Python 3 is installed:

```bash
python3 skills/redact-demo-recording/test_build_filtergraph.py
# or, from that directory:
pytest test_build_filtergraph.py
```

Any change to `build_filtergraph.py` should keep these green.
