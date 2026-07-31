import importlib.resources
import json


def truncate(s, n=60):
    return s if len(s) <= n else s[:n] + "…"


def label_for(entry):
    rpc_short = entry["rpc"].split("/")[-1]
    p = entry["payload"] or {}
    parts = [rpc_short]
    if "plan" in p:
        plan = p["plan"]
        if "command" in plan and "sql_command" in plan["command"]:
            sql = plan["command"]["sql_command"].get("sql", "")
            parts.append(truncate(sql, 40))
        elif "root" in plan:
            root = plan["root"]
            node = next((k for k in root if k not in ("common",)), None)
            if node:
                parts.append(node)
    elif "sql_command_result" in p:
        parts.append("sql_command_result")
    elif "arrow_batch" in p:
        rows = p["arrow_batch"].get("row_count", "?")
        parts.append(f"arrow_batch rows={rows}")
    elif "result_complete" in p:
        parts.append("result_complete")
    elif "metrics" in p:
        parts.append("metrics")
    elif "schema" in p:
        parts.append("schema")
    elif "pairs" in p:
        pairs = p["pairs"]
        if pairs:
            parts.append(f"{pairs[0]['key']}={pairs[0].get('value','')}")
    elif "release_until" in p:
        parts.append("release_until")
    elif "release_all" in p:
        parts.append("release_all")
    return "<br/>".join(parts)


def build_mermaid(entries):
    lines = ["sequenceDiagram", "    participant Client", "    participant Server"]
    op_index = {}

    for entry in entries:
        op_id = (entry["payload"] or {}).get("operation_id", "")
        if op_id and op_id not in op_index:
            op_index[op_id] = len(op_index)

    for entry in entries:
        label = label_for(entry).replace('"', "'")
        p = entry["payload"] or {}
        op_id = p.get("operation_id", "")
        ts = entry["timestamp"].split(" ")[1]

        if entry["direction"] == "Received RPC request":
            lines.append(f"    Client->>Server: [{ts}] {label}")
        else:
            lines.append(f"    Server-->>Client: [{ts}] {label}")

        if op_id:
            lines.append(f"    Note over Client,Server: op={op_id}")

    return "\n".join(lines)


def build_html(entries, log_path):
    with importlib.resources.open_text("scwire.templates", "trace.html", encoding="utf-8") as fh:
        template = fh.read()

    op_ids = sorted({(e["payload"] or {}).get("operation_id", "") for e in entries if e["payload"]})
    op_ids = [o for o in op_ids if o]
    filter_options = "\n".join(
        f'<option value="{o}">{o} '
        f'({sum(1 for e in entries if (e["payload"] or {}).get("operation_id") == o)} events)</option>'
        for o in op_ids
    )

    return (
        template
        .replace("@@LOG_PATH@@", log_path)
        .replace("@@FILTER_OPTIONS@@", filter_options)
        .replace("@@ENTRIES_JSON@@", json.dumps(entries, indent=2))
    )
