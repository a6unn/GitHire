#!/usr/bin/env python3
import os
from pathlib import Path

# Mapping of old names to new names
screenshots_mapping = {
    "Screenshot 2025-10-11 at 12.53.10 PM.png": "01-login.png",
    "Screenshot 2025-10-11 at 1.03.38 PM.png": "02-dashboard.png",
    "Screenshot 2025-10-11 at 12.56.01 PM.png": "03-create-project-step1.png",
    "Screenshot 2025-10-11 at 12.57.21 PM.png": "04-create-project-step2.png",
    "Screenshot 2025-10-11 at 12.58.50 PM.png": "05-project-sourced.png",
    "Screenshot 2025-10-11 at 1.00.28 PM.png": "06-ranking-results.png",
    "Screenshot 2025-10-11 at 1.01.16 PM.png": "07-candidate-detail.png",
    "Screenshot 2025-10-11 at 1.02.19 PM.png": "08-outreach-generation.png",
    "Screenshot 2025-10-11 at 1.03.17 PM.png": "09-my-projects.png",
}

screenshots_dir = Path("/Users/arunkumar/ClaudeCode-Projects/juicebox/screenshots")

for old_name, new_name in screenshots_mapping.items():
    old_path = screenshots_dir / old_name
    new_path = screenshots_dir / new_name

    if old_path.exists():
        old_path.rename(new_path)
        print(f"✓ Renamed: {old_name} → {new_name}")
    else:
        print(f"✗ Not found: {old_name}")

print("\n✨ Screenshot renaming complete!")
print("\nFinal screenshots:")
for file in sorted(screenshots_dir.glob("*.png")):
    if not file.name.startswith("Screenshot"):
        print(f"  {file.name}")
