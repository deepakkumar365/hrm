
from app import app, db
from alembic.script import ScriptDirectory

with app.app_context():
    config = app.extensions['migrate'].migrate.get_config(None)
    script = ScriptDirectory.from_config(config)
    heads = script.get_heads()
    print(f"\n--- ALEMBIC HEADS ({len(heads)}) ---")
    for head in heads:
        print(f"HEAD: {head}")
    print("--- END HEADS ---\n")
