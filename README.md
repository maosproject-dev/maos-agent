**CTO here.**

Here is the `README.md`.

It is written to be "Marketing-Engineering" aligned. It doesn't just say *how* to use it; it explains *why* a developer needs it (to stop their agents from dying silently on Spot instances).

I’ve added badges, a clear "Quick Start," and a section linking the metrics directly to the Grafana dashboard we just built.

---

# Maos Agent SDK

The official Python SDK for building resilient, observable AI Agents on the **Maos Platform**.

**`maos-agent`** provides the "Day 2" primitives required to run autonomous agents in production:

1. **Zero-Config Telemetry:** Automatically emits Prometheus metrics for every tool call, token used, and cognitive step.
2. **Spot Instance Resilience:** Handles `SIGTERM` signals from Kubernetes to allow graceful state checkpointing before node termination.

---

## Installation

```bash
pip install maos-agent

```

---

## Quick Start

Wrap your existing agent code with the Maos decorators to instantly get Grafana dashboards and Spot interruption protection.

```python
import time
import random
from maos_agent import MaosAgent, SpotInterruptionError

# 1. Initialize (Starts Prometheus server on port 8000)
agent = MaosAgent(service_name="financial-analyst", version="v1.2")

# 2. Define Tools (Auto-tracked for success/failure rates)
@agent.tool(name="stock_lookup")
def get_stock_price(ticker: str):
    # Simulate work
    if random.random() < 0.05:
        raise ConnectionError("API Timeout") # Recorded as 'error' in Grafana
    return 150.00

# 3. The Agent Loop
def run_job():
    # Track duration, steps, and success automatically
    with agent.task("analyze_portfolio") as task:
        print("Starting analysis...")
        
        for i in range(5):
            # --- THE MAOS GUARANTEE ---
            # Checks if K8s sent a termination signal (Spot reclaim).
            # Raises SpotInterruptionError if node is draining.
            agent.check_health() 
            
            # Record a "cognitive step" (thinking loop)
            task.step() 
            
            price = get_stock_price("AAPL")
            time.sleep(1)

if __name__ == "__main__":
    try:
        run_job()
    except SpotInterruptionError:
        print("🚨 SPOT RECLAIM DETECTED! SAVING STATE TO REDIS...")
        # Checkpoint your agent's memory here so it can resume on a new node
        exit(0)

```

---

## Key Features

### 1. Automatic Telemetry (The "Brain Scan")

Stop guessing if your agent is working. The SDK automatically exposes a `/metrics` endpoint on port `8000` (configurable) with standard Prometheus metrics:

| Metric Name | Type | Description |
| --- | --- | --- |
| `maos_agent_tool_calls_total` | Counter | Tracks tool usage + Success/Error rates. |
| `maos_agent_steps_per_goal` | Histogram | Detects "Loops of Death" (agents spinning in circles). |
| `maos_agent_token_usage_total` | Counter | Tracks cost (Input vs Output tokens). |
| `maos_agent_task_duration_seconds` | Histogram | End-to-end latency of jobs. |

*Compatible with the [Maos Agent Quality Dashboard](https://www.google.com/search?q=https://github.com/maos-ai/platform/tree/main/dashboards).*

### 2. Graceful Shutdown (The "Money Saver")

Maos runs agents on Spot Instances to save you 90% on compute. However, Spot nodes can disappear with a 2-minute warning.

The `agent.check_health()` method abstracts the complexity of Kubernetes signal handling.

* **Normal operation:** Returns immediately.
* **During Drain:** Raises `SpotInterruptionError`.

**Best Practice:** Call `check_health()` inside your main `while` loop or before every LLM call.

---

## Configuration

You can configure the agent via environment variables or constructor arguments.

| Environment Variable | Default | Description |
| --- | --- | --- |
| `MAOS_SERVICE_NAME` | `unknown-agent` | The name of your agent (for filtering in Grafana). |
| `MAOS_METRICS_PORT` | `8000` | Port to expose Prometheus metrics. |
| `MAOS_LOG_LEVEL` | `INFO` | Logging verbosity. |

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](https://www.google.com/search?q=CONTRIBUTING.md) for details.

1. Fork the repo.
2. Create a feature branch (`git checkout -b feature/langchain-integration`).
3. Commit your changes.
4. Open a Pull Request.

---

**Built by [Maosproject Platform](https://www.google.com/search?q=https://maosproject.io) — The Control Plane for Autonomous Compute.**