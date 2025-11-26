#!/usr/bin/env python3
import os

# Read the original routes.py
file_path = 'D:/Projects/HRMS/hrm/routes.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find the truncated line
if "record.clock_in.strftime('%H:%M') if" in content:
    print("✅ Found the truncated line")
    
    # Replace from the incomplete part onwards
    old_part = """                events_dict[record.date] = {
                    'date': record.date.isoformat(),
                    'status': record.status,
                    'clock_in': record.clock_in.strftime('%H:%M') if"""
    
    new_part = """                events_dict[record.date] = {
                    'date': record.date.isoformat(),
                    'status': record.status,
                    'clock_in': record.clock_in.strftime('%H:%M') if record.clock_in else 'N/A',
                    'clock_out': record.clock_out.strftime('%H:%M') if record.clock_out else 'N/A'
                }
        
        # Convert to list and return
        events_list = list(events_dict.values())
        return jsonify(events_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500"""
    
    # Make sure we find the old part exactly
    if old_part in content:
        content = content.replace(old_part, new_part)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ File fixed successfully!")
        print("✅ Syntax error should be resolved!")
    else:
        print("❌ Could not find the exact text to replace")
        print("Attempting alternative approach...")
        
        # Find the start of the truncated line
        truncate_pos = content.find("record.clock_in.strftime('%H:%M') if")
        if truncate_pos != -1:
            print(f"Found truncate position at character {truncate_pos}")
            # Cut the file at this point and add the proper ending
            content = content[:truncate_pos] + """record.clock_in.strftime('%H:%M') if record.clock_in else 'N/A',
                    'clock_out': record.clock_out.strftime('%H:%M') if record.clock_out else 'N/A'
                }
        
        # Convert to list and return
        events_list = list(events_dict.values())
        return jsonify(events_list)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500"""
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print("✅ File fixed with alternative method!")
else:
    print("❌ Truncated line not found in file")