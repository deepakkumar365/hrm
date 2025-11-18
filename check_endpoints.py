#!/usr/bin/env python
from app import app
import routes

print("All registered endpoints:")
for rule in app.url_map.iter_rules():
    print(f"  Endpoint: {rule.endpoint:30} | Route: {rule.rule}")