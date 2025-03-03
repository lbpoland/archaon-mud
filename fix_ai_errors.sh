#!/bin/bash
# fix_ai_errors.sh - Patch ai_handler.py and initialize AO knowledge file

# Fix 1: Improve scrape_web to handle errors gracefully
sed -i '/async def scrape_web(self, url: str) -> Optional\[Dict\]:/a\    try:' /mnt/home2/mud/ai/ai_handler.py
sed -i '/async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:/i\        async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:' /mnt/home2/mud/ai/ai_handler.py
sed -i '/if response.status == 200:/i\            if response.status == 200:' /mnt/home2/mud/ai/ai_handler.py
sed -i '/logger.error(f"Scrape failed for {{url}}: Status {{response.status}}")/i\                logger.error(f"Scrape failed for {url}: Status {response.status}")' /mnt/home2/mud/ai/ai_handler.py
sed -i '/return None/a\            return None\n    except Exception as e:\n        logger.error(f"Scrape error for {url}: {str(e)}")\n        return None' /mnt/home2/mud/ai/ai_handler.py

# Fix 2: Initialize AO knowledge file if empty or invalid
if [ ! -s /mnt/home2/mud/ai/knowledge/ao_knowledge.json ] || ! grep -q "{" /mnt/home2/mud/ai/knowledge/ao_knowledge.json; then
    echo '{"mechanics": {}, "lore": {}, "tasks": [], "projects": {}}' > /mnt/home2/mud/ai/knowledge/ao_knowledge.json
    chmod 666 /mnt/home2/mud/ai/knowledge/ao_knowledge.json
    echo "Initialized ao_knowledge.json with default JSON"
fi

echo "Applied fixes to ai_handler.py and AO knowledge file"
