#!/usr/bin/env python
# Fix truncated routes.py file

# Read the incomplete file
with open('D:/DEV/HRM/hrm/routes.py', 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Complete the truncated function - start from line 2830 (index 2829)
# We need to reconstruct from line 2831 onwards

fixed_lines = lines[:2830]  # Keep everything up to line 2830

# Add the complete fixed section
fixed_lines.extend([
    "\n",
    "        # Then, add attendance records, only if a leave is not already on that day\n",
    "        for record in attendance_records:\n",
    "            if record.date not in events_dict:\n",
    "                events_dict[record.date] = {\n",
    "                    'date': record.date.isoformat(),\n",
    "                    'status': record.status,\n",
    "                    'clock_in': record.clock_in.strftime('%H:%M') if record.clock_in else 'N/A',\n",
    "                    'clock_out': record.clock_out.strftime('%H:%M') if record.clock_out else 'N/A'\n",
    "                }\n",
    "        \n",
    "        # Convert to list and return\n",
    "        events_list = list(events_dict.values())\n",
    "        return jsonify(events_list)\n",
    "    \n",
    "    except Exception as e:\n",
    "        return jsonify({'error': str(e)}), 500\n",
])

# Write the fixed file
with open('D:/DEV/HRM/hrm/routes.py', 'w', encoding='utf-8') as f:
    f.writelines(fixed_lines)

print(f"✓ File fixed! Total lines: {len(fixed_lines)}")
print(f"✓ Last 5 lines:")
for i, line in enumerate(fixed_lines[-5:]):
    print(f"  {len(fixed_lines)-5+i+1}: {line.rstrip()}")