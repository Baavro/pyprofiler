# ⏱️ PyProfiler - Simple, Powerful Python Profiling

**Lightweight, zero-dependency profiling for Python applications**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Why PyProfiler?

Most Python profilers are either:
- ❌ Too complex (cProfile, line_profiler)
- ❌ Too heavy (require C extensions)
- ❌ Not real-time (only post-analysis)
- ❌ Hard to understand output

**PyProfiler is different:**
- ✅ **Simple**: Context managers and decorators
- ✅ **Lightweight**: Pure Python, zero dependencies
- ✅ **Real-time**: See slow operations as they happen
- ✅ **Beautiful output**: Human-readable summaries
- ✅ **Exportable**: JSON for custom analysis
- ✅ **Nested timing**: See call hierarchies
- ✅ **Async-friendly**: Works with asyncio

---

## Quick Start

### Installation

```bash
pip install pyprofiler  # Once published

# Or from source
git clone https://github.com/yourusername/pyprofiler.git
cd pyprofiler
pip install -e .
```

### Basic Usage

```python
from pyprofiler import Profiler, time_block, checkpoint

profiler = Profiler()

# Time a block of code
with time_block("data_processing"):
    process_data()

# Mark checkpoints
checkpoint("data_loaded", records=1000)

# Print summary
profiler.print_summary()
```

**Output:**
```
⏱️  PROFILING SUMMARY
================================================================================
📊 Total Time: 5.42s

Operation                Total Time    Calls     Avg Time      %
--------------------------------------------------------------------------------
data_processing          5.12s         1         5.12s       94.5%
```

---

## Features

### 1. **Context Manager** - Time Blocks of Code

```python
from pyprofiler import time_block

with time_block("database_query"):
    result = db.query("SELECT * FROM users")

with time_block("api_call", endpoint="https://api.example.com"):
    response = requests.get(endpoint)
```

### 2. **Decorator** - Time Functions

```python
from pyprofiler import get_profiler

profiler = get_profiler()

@profiler.track
def expensive_function():
    # This will be automatically timed
    compute_something()
```

### 3. **Nested Timing** - See Call Hierarchies

```python
with time_block("outer_operation"):
    with time_block("step_1"):
        do_step_1()
    
    with time_block("step_2"):
        do_step_2()
```

**Output:**
```
outer_operation > step_1: 2.34s
outer_operation > step_2: 1.56s
```

### 4. **Checkpoints** - Mark Important Events

```python
from pyprofiler import checkpoint

checkpoint("data_loaded", records=5000)
checkpoint("validation_complete", errors=0)
```

### 5. **Real-Time Feedback** - See Slow Operations

```python
# Operations >5s are automatically shown
with time_block("slow_query"):
    time.sleep(6)

# Output (immediate):
# ⏱️  slow_query: 6.01s
```

### 6. **Export to JSON** - Custom Analysis

```python
profiler.export_json("profile.json")

# Use with analyze_profile.py for detailed analysis
python analyze_profile.py profile.json
```

---

## Use Cases

### Web Applications

```python
from pyprofiler import time_block

@app.route("/api/users")
def get_users():
    with time_block("fetch_users"):
        users = db.query("SELECT * FROM users")
    
    with time_block("serialize"):
        return jsonify(users)

# See which endpoint operations are slow
```

### Data Processing Pipelines

```python
with time_block("data_pipeline"):
    with time_block("extract"):
        data = extract_data()
    
    with time_block("transform"):
        data = transform_data(data)
    
    with time_block("load"):
        load_data(data)

# Identify pipeline bottlenecks
```

### API Integrations

```python
with time_block("external_api_call", service="stripe"):
    response = stripe.Charge.create(...)

with time_block("external_api_call", service="sendgrid"):
    response = sendgrid.send(...)

# Compare API performance
```

### Machine Learning

```python
with time_block("model_training", model="random_forest"):
    model.fit(X_train, y_train)

with time_block("model_inference", batch_size=1000):
    predictions = model.predict(X_test)

# Optimize training and inference
```

---

## Advanced Usage

### Global Profiler

```python
from pyprofiler import get_profiler, time_block

# Use global profiler (singleton)
with time_block("operation"):
    do_work()

# Get profiler instance
profiler = get_profiler()
profiler.print_summary()
```

### Custom Profiler Instance

```python
from pyprofiler import Profiler

# Create separate profiler
profiler = Profiler()

with profiler.time("my_operation"):
    do_work()

profiler.print_summary()
```

### Disable Profiling

```python
from pyprofiler import Profiler

# Disable for production
profiler = Profiler(enabled=False)

# No overhead - profiling calls are no-ops
with profiler.time("operation"):
    do_work()
```

### Async Support

```python
import asyncio
from pyprofiler import time_block

async def async_operation():
    with time_block("async_fetch"):
        await asyncio.sleep(1)
    
    with time_block("async_process"):
        await process_data()

asyncio.run(async_operation())
```

---

## Output Formats

### Summary View

```
⏱️  PROFILING SUMMARY
================================================================================

📊 Total Time: 125.67s (2.09m)

Operation                                Total Time    Calls     Avg Time      %
--------------------------------------------------------------------------------
database_queries                         78.45s        120       0.65s       62.4%
api_calls                               32.12s         45       0.71s       25.6%
data_processing                         15.10s         10       1.51s       12.0%
```

### Slowest Operations

```
Slowest Operations                                               Time
--------------------------------------------------------------------------------
database_queries > fetch_users                                 12.34s
api_calls > stripe_charge                                       5.67s
data_processing > transform                                     3.45s
```

### Checkpoints

```
📍 Checkpoints:
   CHECKPOINT: batch_1_complete {'records_processed': 1000}
   CHECKPOINT: validation_complete {'errors': 0}
```

---

## Analysis Tool

Use the included analyzer for deep insights:

```bash
python -m pyprofiler.analyze profile.json
```

**Output:**
```
🔍 PROFILING ANALYSIS
================================================================================

TOP BOTTLENECKS
1. database_queries (62.4% of time)
   💡 Optimization: Add indexes or use connection pooling

2. api_calls (25.6% of time)
   💡 Optimization: Use async requests or batch calls

TIMELINE ANALYSIS
Activity by time (10s buckets):
Time         Operations    Total Time
----------------------------------------
0s-10s       15            8.45s
10s-20s      22            12.34s
```

---

## API Reference

### `Profiler(enabled=True)`

Main profiler class.

**Methods:**
- `time(name, **metadata)` - Context manager for timing
- `track(func)` - Decorator for timing functions
- `checkpoint(name, **metadata)` - Mark an event
- `print_summary(top_n=20)` - Print summary report
- `export_json(filepath)` - Export to JSON
- `get_stats()` - Get statistics dict

### `time_block(name, **metadata)`

Convenient context manager using global profiler.

```python
with time_block("operation", param=value):
    do_work()
```

### `checkpoint(name, **metadata)`

Mark a checkpoint using global profiler.

```python
checkpoint("milestone", count=1000)
```

### `get_profiler()`

Get or create global profiler instance.

```python
profiler = get_profiler()
```

---

## Configuration

### Threshold for Real-Time Display

```python
# Change threshold (default: 5 seconds)
# In profiler.py, modify:
if duration > 5.0:  # Change to your threshold
    print(f"⏱️  {full_name}: {duration:.2f}s")
```

### Output Format

```python
# Customize summary format
profiler.print_summary(top_n=30)  # Show top 30 instead of 20
```

---

## Comparison

| Feature | PyProfiler | cProfile | line_profiler | py-spy |
|---------|-----------|----------|---------------|---------|
| Zero dependencies | ✅ | ✅ | ❌ | ❌ |
| Real-time output | ✅ | ❌ | ❌ | ✅ |
| Easy to use | ✅ | ❌ | ❌ | ✅ |
| Nested timing | ✅ | ❌ | ❌ | ❌ |
| Custom metadata | ✅ | ❌ | ❌ | ❌ |
| Async-friendly | ✅ | ⚠️ | ⚠️ | ✅ |
| Line-level | ❌ | ❌ | ✅ | ✅ |

**Use PyProfiler when:**
- You want simple, readable profiling
- You need real-time feedback
- You're profiling async code
- You want zero setup overhead

**Use other tools when:**
- You need line-level profiling (line_profiler)
- You need C-level profiling (py-spy)
- You need statistical profiling (cProfile)

---

## Examples

### Web Framework Middleware

```python
from flask import Flask
from pyprofiler import Profiler

app = Flask(__name__)
profiler = Profiler()

@app.before_request
def start_profiling():
    request.profiler = Profiler()

@app.after_request
def end_profiling(response):
    request.profiler.print_summary()
    return response

@app.route("/")
def index():
    with request.profiler.time("database"):
        users = get_users()
    return render_template("index.html", users=users)
```

### CLI Application

```python
import click
from pyprofiler import Profiler, time_block

@click.command()
@click.option("--profile", is_flag=True)
def main(profile):
    if profile:
        with time_block("full_operation"):
            run_application()
    else:
        run_application()

if __name__ == "__main__":
    main()
```

### Background Job

```python
from pyprofiler import time_block, checkpoint

def process_queue():
    with time_block("queue_processing"):
        while True:
            with time_block("process_item"):
                item = queue.get()
                process(item)
                checkpoint("item_processed", queue_size=queue.size())

            if queue.empty():
                break
```

---

## Contributing

We welcome contributions! Areas we'd love help with:

- 📊 Visualization (web-based dashboard)
- 📈 Grafana/Prometheus integration
- 🎨 More output formats (HTML, CSV)
- 🔧 Performance optimizations
- 📖 More examples and use cases

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License - see [LICENSE](LICENSE) file.

---

## Credits

Created for [Omnilingual Language Finder](https://github.com/yourusername/omnilingual-finder), extracted as standalone library for community use.

---

## Roadmap

- [ ] v1.0: Core functionality (✅ Done!)
- [ ] v1.1: HTML output format
- [ ] v1.2: Memory profiling
- [ ] v1.3: Integration with logging libraries
- [ ] v2.0: Web dashboard
- [ ] v2.1: Grafana exporter
- [ ] v2.2: Distributed tracing support

---

<div align="center">

**⏱️ Make your Python code faster, one profile at a time**

[⭐ Star this repo](https://github.com/yourusername/pyprofiler) • [🐛 Report Bug](https://github.com/yourusername/pyprofiler/issues) • [💡 Request Feature](https://github.com/yourusername/pyprofiler/issues)

</div>
