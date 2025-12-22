# Fix corrupted CSS file by removing null bytes and corrupted section
with open('static/css/styles.css', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Keep lines 1-3932 (before corruption) and lines 4912-end (clean Zoho CSS)
clean_lines = lines[:3932] + lines[4911:]

# Write back
with open('static/css/styles.css', 'w', encoding='utf-8') as f:
    f.writelines(clean_lines)

print(f"Fixed CSS file. Removed {4911 - 3932} corrupted lines.")
print(f"New file has {len(clean_lines)} lines.")
