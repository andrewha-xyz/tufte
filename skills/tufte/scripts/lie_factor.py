#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Lie factor = (size of effect shown in graphic) / (size of effect in data).  VDQI p. 57.

    uv run --locked "<skill dir>/scripts/lie_factor.py" --data 18 27.5 --graphic 0.6 5.3

  effect in data    = (27.5 - 18) / 18   = 0.528
  effect in graphic = (5.3 - 0.6) / 0.6  = 7.833
  lie factor        = 7.833 / 0.528      = 14.8   (Tufte's fuel-economy example)

Graphic sizes can be any consistent unit: pixels, mm, inches, bar length, radius.
For an area-encoded mark pass the AREA, not the radius, or the lie is hidden.
Exit 0 if 0.95 <= LF <= 1.05, 1 if distorted, 2 on usage error.
"""
import sys


def effect(a, b):
    return (b - a) / a


def main(argv):
    if "--data" not in argv or "--graphic" not in argv:
        print(__doc__)
        return 2
    d = argv.index("--data")
    g = argv.index("--graphic")
    try:
        d0, d1 = float(argv[d + 1]), float(argv[d + 2])
        g0, g1 = float(argv[g + 1]), float(argv[g + 2])
    except (IndexError, ValueError):
        print("need two numbers after each flag")
        return 2
    if d0 == 0 or g0 == 0:
        print("first value of each pair must be non-zero (effect is relative)")
        return 2
    ed, eg = effect(d0, d1), effect(g0, g1)
    if ed == 0 and eg == 0:
        print("no change in data and none in graphic: lie factor undefined, nothing distorted")
        return 0
    if ed == 0:
        print(f"no change in data but the graphic changes by {eg:+.3f}: lie factor undefined, DISTORTED")
        return 1
    lf = eg / ed
    ok = 0.95 <= lf <= 1.05
    print(f"effect in data   : {ed:+.3f}")
    print(f"effect in graphic: {eg:+.3f}")
    print(f"lie factor       : {lf:.2f}  ({'OK' if ok else 'DISTORTED'})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
