import json
import os
import sys

sys.dont_write_bytecode = True

def read_embed(filename):
    filepath = os.path.join('embeds', filename)
    
    try:
        with open(filepath, 'r') as file:
            data = json.load(file)
            
            title = data.get('title', 'No Title')
            description = data.get('description', 'No Description')
            fields = data.get('fields', {})

            return {
                'title': title,
                'description': description,
                'fields': fields
            }
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file {filename}.")
        return None
