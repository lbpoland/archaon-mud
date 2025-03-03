#!/bin/bash
# Fix ai_handler.py logging attribute from 'filename' to 'baseFilename'
sed -i "s/handler.filename.endswith('working_tasks.log')/handler.baseFilename.endswith('working_tasks.log')/g" /mnt/home2/mud/ai/ai_handler.py
echo "Fixed 'filename' to 'baseFilename' in ai_handler.py"
