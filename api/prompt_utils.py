import re

def extract_json(text):
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return match.group(0)
    match_list = re.search(r'\[[\s\S]*\]', text)
    if match_list:
        return match_list.group(0)
    return text
