from __future__ import annotations

import json
from training.evaluate import compare_agents

if __name__ == "__main__":
    print(json.dumps(compare_agents(20), indent=2))
