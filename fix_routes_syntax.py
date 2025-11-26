#!/usr/bin/env python3
"""
Fix the truncated routes.py file - complete the api_attendance_calendar_data function
"""

# Read the current routes.py file
with open('routes.py', 'r') as f:
    lines = f.readlines()

print(f"Original file has {len(lines)} lines")

# Find where the broken function ends (line with 'clock_in': record.clock_in.strftime)
# This is around line 2836
truncate_line = None
for i, line in enumerate(lines):
    if "record.clock_in.strftime('%H:%M') if" in line:
        truncate_line = i
        print(f"Found incomplete line at index {i} (line {i+1})")
        break

if truncate_line is None:
    print("ERROR: Could not find the incomplete line")
    exit(1)

# Remove everything from the incomplete line onwards
lines = lines[:truncate_line]

# Now add the complete function ending
completion = """                    'clock_in': record.clock_in.strftime('%H:%M') if record.clock_in else 'N/A',
                    'clock_out': record.clock_out.strftime('%H:%M') if record.clock_out else 'N/A'
                }
        
        # Convert to list and return
        events_list = list(events_dict.values())
        return jsonify(events_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
"""

lines.append(completion)

# Write back
with open('routes.py', 'w') as f:
    f.writelines(lines)

print(f"Fixed! New file has {len(lines)} lines")
print("✅ Syntax fix complete!")