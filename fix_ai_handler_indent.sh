
#!/bin/bash
# fix_ai_handler_indent.sh - Fix indentation and scraping in ai_handler.py

# Backup original file
cp /mnt/home2/mud/ai/ai_handler.py /mnt/home2/mud/ai/ai_handler.py.bak

# Replace scrape_web with properly indented version
sed -i '/async def scrape_web(self, url: str) -> Optional\[Dict\]:/{N;s/async def scrape_web(self, url: str) -> Optional\[Dict\]:\n    try:/async def scrape_web(self, url: str) -> Optional[Dict]:\n    try:/;};/async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:/,/return None/{s/^\s\+//;s/async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:/        async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=60)) as response:/;s/if response.status == 200:/            if response.status == 200:/;s/logger.error(f"Scrape failed for {url}: Status {response.status}")/                logger.error(f"Scrape failed for {url}: Status {response.status}")/g;s/return None/            return None\n        except Exception as e:\n            logger.error(f"Scrape error for {url}: {str(e)}")\n            return None/}' /mnt/home2/mud/ai/ai_handler.py

# Ensure AO knowledge file exists (redundant check from last script)
if [ ! -s /mnt/home2/mud/ai/knowledge/ao_knowledge.json ] || ! grep -q "{" /mnt/home2/mud/ai/knowledge/ao_knowledge.json; then
    echo '{"mechanics": {}, "lore": {}, "tasks": [], "projects": {}}' > /mnt/home2/mud/ai/knowledge/ao_knowledge.json
    chmod 666 /mnt/home2/mud/ai/knowledge/ao_knowledge.json
    echo "Initialized ao_knowledge.json with default JSON"
fi

echo "Fixed indentation and scraping in ai_handler.py"
