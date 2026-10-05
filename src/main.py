import sys


def main() -> int:
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A_PATH B_PATH", file=sys.stderr)
        return 2
    command, a_path, b_path = sys.argv[1:]
    # TODO: read both files as raw bytes (brief, Section 2), then print the listing.
    return 0


raise SystemExit(main())


def read_lines(path):
    with open(path, "rb") as f:          # "rb" = raw bytes. Text mode breaks \r\n tests
        data = f.read()
    lines = data.split(b"\n")
    if lines[-1] == b"":                 # a final newline makes no extra line
        lines.pop()
    return lines


def myers(a, b):
    """Return the edit script from a to b as a list of ' ', '-', '+'."""
    n = len(a)
    m = len(b)
    max_d = n + m
    offset = max_d + 1                   # V[k] is stored at v[k + offset] (k can be negative)
    v = [0] * (2 * max_d + 3)
    trace = []                           # trace[d] = V after round d, for k in -d..d

    for d in range(max_d + 1):
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[k - 1 + offset] < v[k + 1 + offset]):
                x = v[k + 1 + offset]            # down (insert): x stays the same
            else:
                x = v[k - 1 + offset] + 1        # right (delete): x goes up by one
            y = x - k
            while x < n and y < m and a[x] == b[y]:   # the snake
                x += 1
                y += 1
            v[k + offset] = x
            if x >= n and y >= m:
                trace.append(v[offset - d: offset + d + 1])
                return backtrack(trace, n, m)
        trace.append(v[offset - d: offset + d + 1])
