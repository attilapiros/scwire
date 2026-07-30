import json
import re

LOG_RE = re.compile(
    r"(\d+/\d+/\d+ \d+:\d+:\d+) INFO LoggingInterceptor: (Received RPC request|Responding to RPC) "
    r"([\w.]+/[\w]+) \(id \d+\):"
)


def extract_entries(path):
    with open(path) as f:
        lines = f.readlines()

    entries = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = LOG_RE.search(line)
        if m:
            timestamp, direction, rpc = m.group(1), m.group(2), m.group(3)
            i += 1
            payload = None
            if i < len(lines) and lines[i].strip().startswith("{"):
                json_lines = []
                depth = 0
                while i < len(lines):
                    json_lines.append(lines[i])
                    depth += lines[i].count("{") - lines[i].count("}")
                    i += 1
                    if depth == 0:
                        break
                try:
                    payload = json.loads("".join(json_lines))
                except json.JSONDecodeError:
                    payload = {"raw": "".join(json_lines)}
            entries.append({
                "timestamp": timestamp,
                "direction": direction,
                "rpc": rpc,
                "payload": payload,
            })
        else:
            i += 1
    return entries
