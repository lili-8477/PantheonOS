#!/usr/bin/env python
"""
Code Distillation via Evolution.

Evolve Python code to match a black-box ML model's predictions.
Uses Pantheon Evolution framework with MAP-Elites.

Usage:
    python run.py [--iterations N] [--output DIR]
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Load environment
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Set data directory for evaluator (must be absolute path)
example_dir = Path(__file__).resolve().parent
os.environ["CODE_DISTILLATION_DATA_DIR"] = str(example_dir / "data")


async def run_evolution(
    iterations: int = 100,
    output_dir: str = None,
    resume: str = None,
):
    """Run code distillation evolution."""
    from pantheon.evolution import EvolutionTeam, EvolutionConfig
    from pantheon.evolution.program import CodebaseSnapshot

    example_dir = Path(__file__).parent

    # Load initial code and evaluator
    initial_code = CodebaseSnapshot.from_single_file(
        "distilled_code.py",
        (example_dir / "distilled_code.py").read_text()
    )
    evaluator_code = (example_dir / "evaluator.py").read_text()

    # Configuration
    output_path = example_dir / "results" if output_dir is None else Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    config = EvolutionConfig(
        max_iterations=iterations,
        num_workers=8,
        num_islands=2,
        num_inspirations=2,
        num_top_programs=3,
        max_parallel_evaluations=2,
        evaluation_timeout=120,
        analyzer_timeout=180,  # Longer timeout for Python analysis
        feature_dimensions=["fidelity"],
        early_stop_generations=50,
        function_weight=1.0,
        llm_weight=0.0,
        log_level="INFO",
        checkpoint_interval=10,
        db_path=str(output_path),
        # Enable Python interpreter for analyzer to inspect model weights
        analyzer_use_python=True,
        analyzer_python_workdir=str(example_dir),
    )

    # Optimization objective
    objective = """Distill the CellTypist classifier into interpretable Python code.

## Goal
Maximize fidelity (agreement rate with CellTypist model). Target: >= 95%

## Cell Types (EXACT NAMES required):
- Plasma cells, Mast cells, DC1, Kupffer cells, pDC
- gamma-delta T cells, Endothelial cells, Follicular B cells
- Alveolar macrophages, Neutrophil-myeloid progenitor

## STRICT CONSTRAINTS (IMPORTANT!)
The distilled code must be SELF-CONTAINED and INDEPENDENT:
- DO NOT import celltypist or load any .pkl model files
- DO NOT load external weight files at runtime
- All decision logic must be hardcoded in the Python code itself
- The code should work without any external model files

## Hints
- The analyzer has Python capability to run experiments and inspect the model
- Use the analyzer to extract knowledge (weights, thresholds, feature importance)
- Then hardcode that knowledge into simple, interpretable rules
- Consider: marker genes, decision trees, threshold-based rules

## Requirements
1. Function signature: def predict_cell_type(expression: dict) -> str
2. Return one of the exact cell type names listed above
3. Maximize fidelity with the original model
4. Code must be self-contained (no external model dependencies)
"""

    print("=" * 60)
    print("Code Distillation via Evolution")
    print("=" * 60)
    print(f"Model: CellTypist Immune_All_Low.pkl")
    print(f"Iterations: {iterations}")
    print(f"Output: {output_path}")
    print()

    # Run evolution
    team = EvolutionTeam(config=config)
    result = await team.evolve(
        initial_code=initial_code,
        evaluator_code=evaluator_code,
        objective=objective,
        resume_from=resume,
    )

    # Save results
    print("\n" + "=" * 60)
    print(result.get_summary())

    # Save best code
    best_code_path = output_path / "distilled_code_best.py"
    best_code_path.write_text(result.best_code)
    print(f"\nBest code saved to: {best_code_path}")

    # Also update the main distilled_code.py
    (example_dir / "distilled_code.py").write_text(result.best_code)

    return result


def main():
    parser = argparse.ArgumentParser(description="Code Distillation via Evolution")
    parser.add_argument("--iterations", "-n", type=int, default=100)
    parser.add_argument("--output", "-o", type=str, default=None)
    parser.add_argument("--resume", "-r", type=str, default=None)

    args = parser.parse_args()

    try:
        result = asyncio.run(run_evolution(
            iterations=args.iterations,
            output_dir=args.output,
            resume=args.resume,
        ))
        print(f"\nFinal fidelity: {result.best_score:.1%}")
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(1)


if __name__ == "__main__":
    main()
