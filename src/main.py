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


def diff(a, b):
    n = len(a)
    m = len(b)
    start = 0
    while start < n and start < m and a[start] == b[start]:
        start += 1
    end_a = n
    end_b = m
    while end_a > start and end_b > start and a[end_a - 1] == b[end_b - 1]:
        end_a -= 1
        end_b -= 1
    middle = diff_middle(a[start:end_a], b[start:end_b])
    return [" "] * start + middle + [" "] * (n - end_a)


def diff_middle(a, b):
    in_a = set(a)
    in_b = set(b)
    keep_a = [i for i in range(len(a)) if a[i] in in_b]    # positions that could match
    keep_b = [j for j in range(len(b)) if b[j] in in_a]
    small_ops = myers([a[i] for i in keep_a], [b[j] for j in keep_b])

    ops = []
    i = 0          # next line of a
    j = 0          # next line of b
    p = 0          # next line of the small a
    q = 0          # next line of the small b
    for op in small_ops:
        if op == " " or op == "-":
            while i < keep_a[p]:       # lines of a we set aside become deletes
                ops.append("-")
                i += 1
        if op == " " or op == "+":
            while j < keep_b[q]:       # lines of b we set aside become inserts
                ops.append("+")
                j += 1
        ops.append(op)
        if op != "+":
            i += 1
            p += 1
        if op != "-":
            j += 1
            q += 1
    ops += ["-"] * (len(a) - i)
    ops += ["+"] * (len(b) - j)
    return ops


def to_ranges(positions):
    """[3, 4, 5, 9] -> '3-6,9-10'.  Empty -> '.'"""
    if not positions:
        return "."
    parts = []
    start = positions[0]
    end = start + 1
    for p in positions[1:]:
        if p == end:                    # touches the current range: extend it
            end += 1
        else:
            parts.append(f"{start}-{end}")
            start = p
            end = p + 1
    parts.append(f"{start}-{end}")
    return ",".join(parts)


def highlight_line(old, new):
    old = old.decode("utf-8")
    new = new.decode("utf-8")
    ops = diff(old, new)
    old_pos = []
    new_pos = []
    i = 0
    j = 0
    for op in ops:
        if op == " ":
            i += 1
            j += 1
        elif op == "-":
            old_pos.append(i)           # this character of the old line was removed
            i += 1
        else:
            new_pos.append(j)           # this character of the new line was added
            j += 1
    return f"? {to_ranges(old_pos)} | {to_ranges(new_pos)}\n".encode()
