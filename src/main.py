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


def diff(a, b):
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


def backtrack(trace, n, m):
    ops = []
    x = n
    y = m
    for d in range(len(trace) - 1, 0, -1):
        prev = trace[d - 1]                      # V from round d-1; k is stored at index k + (d-1)
        k = x - y
        if k == -d or (k != d and prev[k - 1 + d - 1] < prev[k + 1 + d - 1]):
            prev_k = k + 1
        else:
            prev_k = k - 1
        prev_x = prev[prev_k + d - 1]
        prev_y = prev_x - prev_k
        while x > prev_x and y > prev_y:         # walk back along the snake
            ops.append(" ")
            x -= 1
            y -= 1
        if x == prev_x:
            ops.append("+")                      # x didn't change, so we came down: insert
        else:
            ops.append("-")                      # we came right: delete
        x = prev_x
        y = prev_y
    while x > 0:                                 # the snake at d = 0
        ops.append(" ")
        x -= 1
        y -= 1
    ops.reverse()                                # built backwards, so flip once at the end
    return ops


def delete_first(ops):
    result = []
    dels = []
    ins = []
    for op in ops:
        if op == "-":
            dels.append(op)
        elif op == "+":
            ins.append(op)
        else:
            result += dels
            result += ins
            dels = []
            ins = []
            result.append(op)
    result += dels
    result += ins
    return result


def render(a, b, ops, with_highlight):
    out = []
    i = 0
    j = 0
    pos = 0
    while pos < len(ops):
        if ops[pos] == " ":
            out.append(b" " + a[i] + b"\n")
            i += 1
            j += 1
            pos += 1
            continue
        dels = []                       # a change block: some '-' then some '+'
        ins = []
        while pos < len(ops) and ops[pos] == "-":
            dels.append(a[i])
            i += 1
            pos += 1
        while pos < len(ops) and ops[pos] == "+":
            ins.append(b[j])
            j += 1
            pos += 1
        for line in dels:
            out.append(b"-" + line + b"\n")
        for t, line in enumerate(ins):
            out.append(b"+" + line + b"\n")
            if with_highlight and t < len(dels):
                out.append(highlight_line(dels[t], line))   # Part B, Step 7
    return b"".join(out)


def main():
    if len(sys.argv) != 4 or sys.argv[1] not in ("lines", "highlight"):
        print("usage: main.py lines|highlight A B", file=sys.stderr)
        sys.exit(2)
    try:
        a = read_lines(sys.argv[2])
        b = read_lines(sys.argv[3])
    except OSError as e:                       # can't read a file: nothing on stdout, exit code 2
        print(f"error: {e}", file=sys.stderr)
        sys.exit(2)
    ops = delete_first(diff(a, b))
    sys.stdout.buffer.write(render(a, b, ops, sys.argv[1] == "highlight"))


if __name__ == "__main__":
    main()
