#!/bin/bash
# fix_ai_logs.sh - Fix AO JSON, log formatting, and add website scraping log

# Backup ai_handler.py
cp /mnt/home2/mud/ai/ai_handler.py /mnt/home2/mud/ai/ai_handler.py.bak2

# Fix 1: Reinitialize ao_knowledge.json with valid JSON
echo '{"mechanics": {}, "lore": {}, "tasks": [], "projects": {}}' > /mnt/home2/mud/ai/knowledge/ao_knowledge.json
chmod 666 /mnt/home2/mud/ai/knowledge/ao_knowledge.json
echo "Reinitialized ao_knowledge.json with valid JSON"

# Fix 2: Tidy log formatting with newlines
sed -i "s/format='%(asctime)s - %(levelname)s - %(message)s'/format='%(asctime)s - %(levelname)s - %(message)s\\n'/" /mnt/home2/mud/ai/ai_handler.py
sed -i "s/format='%(asctime)s - %(message)s'/format='%(asctime)s - %(message)s\\n'/" /mnt/home2/mud/ai/ai_handler.py
echo "Updated log formatting for readability"

# Fix 3: Add website_scraped.log and log successful scrapes
sed -i '/ai_edited_handler = logging.FileHandler/a\ai_scraped_handler = logging.FileHandler("/mnt/home2/mud/logs/website_scraped.log")\nai_scraped_handler.setLevel(logging.INFO)\nai_scraped_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s\\n"))\nlogger.addHandler(ai_scraped_handler)' /mnt/home2/mud/ai/ai_handler.py
sed -i '/async def scrape_web(self, url: str) -> Optional\[Dict\]:/a\    async def log_scrape(self, url: str, data: Dict) -> None:\n        logger.info(f"Scraped website: {url}", extra={"level": "scraped"})' /mnt/home2/mud/ai/ai_handler.py
sed -i '/html = await response.text()/a\                    await self.log_scrape(url, {"content_length": len(text)})' /mnt/home2/mud/ai/ai_handler.py
echo "Added website_scraped.log for successful scrapes"

# Fix agent-specific loggers to use extra parameter for custom levels
for agent in ao mystra tyr lolth oghma deneir selune torm vhaeraun azuth; do
    sed -i "/self.logger = logging.getLogger(f'{name}_AI')/a\        self.logger.handlers = []\n        for level, handler in AGENT_LOGGERS[name].items():\n            handler.setLevel(logging.DEBUG if level == 'working' else logging.INFO)\n            self.logger.addHandler(handler)" /mnt/home2/mud/ai/agents/${agent}_ai.py
done
echo "Fixed agent loggers to differentiate outputs"

echo "All fixes applied to ai_handler.py and agent files"
