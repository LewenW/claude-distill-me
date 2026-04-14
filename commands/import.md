---
name: import
description: Import claude.ai exported chat data for pattern analysis
argument-hint: "[path-to-json]"
---

# Import Claude.ai Export Data

Help the user import their claude.ai conversation history for richer pattern extraction.

## Steps

1. Check if the `import/` directory exists in the plugin root. If not, create it.

2. If the user provided a file path argument, copy that JSON file to the `import/` directory.

3. If no path given, explain:
   - Go to claude.ai → Settings → Export Data
   - Download the ZIP, extract it
   - Place the `conversations.json` (or individual chat JSON files) into the plugin's `import/` directory
   - Then re-run `/distill-me:distill` to include this data in the analysis

4. After copying, call `scan_user_data()` to verify the imported data is detected. Report how many exported turns were found.

## File Format

The scanner handles claude.ai export JSON:
- Multi-chat format (array of conversations)
- Single-chat format (one conversation object)
- Each conversation has `chat_messages` with `sender` (human/assistant) and `text` fields
