import importlib.util
import sys
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "costs", Path(__file__).parents[1] / "scripts" / "costs.py"
)
costs = importlib.util.module_from_spec(spec)
sys.modules["costs"] = costs
spec.loader.exec_module(costs)


def test_cost_formula():
    p = costs.Price("X", "m", input=0.15, output=0.80)
    # 3M input + 80k output = 0.45 € + 0.064 €
    assert abs(costs.cost(p, 3_000_000, 80_000) - 0.514) < 1e-9
