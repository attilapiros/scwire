# scwire

Parse and visualize Spark Connect `LoggingInterceptor` logs as an interactive HTML sequence diagram.

## Install

```bash
pip install git+https://github.com/attilapiros/scwire
```

## Usage

### Interactive HTML report

```bash
scwire spark.log --html trace.html
open trace.html
```

The report has two views:

- **Sequence Diagram** — paginated Mermaid diagram of all RPC exchanges
- **Event Table** — searchable table with full payloads

Both views support filtering by `operation_id` and configurable page size.

### Plain text dump

```bash
scwire spark.log
```

Prints each intercepted RPC with its JSON payload.

### As a module

```bash
python -m scwire spark.log --html trace.html
```

### Library

```python
from scwire import extract_entries, build_html

entries = extract_entries("spark.log")
html = build_html(entries, "spark.log")
```

## Starting the Spark Connect server

Launch the server with the `LoggingInterceptor` enabled:

```bash
./sbin/start-connect-server.sh \
  --jars sql/connect/server/target/spark-connect_2.13-5.0.0-SNAPSHOT.jar \
  --conf spark.connect.grpc.interceptor.classes=org.apache.spark.sql.connect.service.LoggingInterceptor
```

The interceptor writes request/response pairs to the Spark log, which is what scwire parses.

## Log format

scwire expects lines emitted by Spark Connect's `LoggingInterceptor`:

```
2024/01/15 10:23:45 INFO LoggingInterceptor: Received RPC request spark.connect.SparkConnectService/ExecutePlan (id 1):
{
  "plan": { ... }
}
```

Both `Received RPC request` and `Responding to RPC` directions are captured.

