def fix_json(json_string):
    """
    Attempts to fix common JSON parsing errors.
    """
    # Remove leading/trailing whitespace
    json_string = json_string.strip()

    # Remove any potential unicode BOM
    json_string = json_string.lstrip('\ufeff')

    # Replace single quotes with double quotes for property names (risky, but might help)
    # json_string = json_string.replace("'", "\"")  #Be careful with this, it can break valid JSON

    # Handle unescaped characters (very basic, expand as needed)
    json_string = json_string.replace('\\"', '"') # replace escaped quotes

    return json_string