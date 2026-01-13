# Single Cell Benchmark

This benchmark evaluates agent performance on various single-cell analysis tasks, including data integration, cell type annotation, multimodal prediction, spatial deconvolution, and data cleaning/analysis.

## Usage

Run the benchmark using the `run_benchmark.py` script in pantheon-agents project root folder.

```bash
python benchmarks/single_cell_benchmark/run_benchmark.py [options]
```

### Arguments

- `--round <NAME>`: Name of the benchmark round. If not provided, a timestamped name (e.g., `round_20240101_120000`) is generated. use to **continue** a previous round.
- `--limit <INT>`: Limit the number of tasks to run (useful for testing).
- `--team <NAME>`: Team template to use (default: `default`).
- `--model <NAME>`: Model override (default: `gemini/gemini-3-flash-preview`).

### Examples

**Run all tasks:**
```bash
python benchmarks/single_cell_benchmark/run_benchmark.py
```

**Run first 5 tasks for testing:**
```bash
python benchmarks/single_cell_benchmark/run_benchmark.py --limit 5
```

**Run with a specific model:**
```bash
python benchmarks/single_cell_benchmark/run_benchmark.py --model "claude-3-5-sonnet"
```

## Structure

- `benchmark.jsonl`: Contains the dataset of tasks and ground truth.
- `benchmark_data/`: (Ignored in git) Contains the actual data files used by tasks.
- `results/`: (Ignored in git) specific benchmark round results.
  - `<round_name>/report.md`: Summary report.
  - `<round_name>/report.json`: JSON report.
  - `<round_name>/<task_id>.json`: Individual task results.
  - `<round_name>/<task_id>_memory.json`: Agent interaction logs.
- `workspaces/`: (Ignored in git) Agent working directories for each task.

## Agent Interface

Agents must use the `submit_answer` tool to complete a task.

```python
def submit_answer(answer: str):
    """
    Submit the final answer for the task.
    Args:
        answer: The final answer. Use string representation for numbers/booleans (e.g., "1.23", "True", "Mast cells").
    """
```
