cd src/promptOptimizer
export OPENROUTER_API_KEY=...   # required for this recipe

cp -n artifacts/scenarios-api.json artifacts/scenarios-api.full.json
uv run python -c "import json;from pathlib import Path;p=Path('artifacts/scenarios-api.json');d=json.loads(p.read_text());s=d.get('scenarios',d);p.write_text(json.dumps({'scenarios':s[:12]},indent=2));print(len(s[:12]))"

FLAGS="--backend openrouter --reflection-backend openrouter --judge reflection --auto light --num-threads 4 --seed 0"

uv run main.py baseline  $FLAGS
uv run main.py bootstrap $FLAGS
uv run main.py show-prompt --task api --program artifacts/api-baseline.json
uv run main.py show-prompt --task api --program artifacts/api-bootstrap.json
