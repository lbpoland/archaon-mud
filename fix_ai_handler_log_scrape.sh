
#!/bin/bash
# fix_ai_handler_log_scrape.sh - Fix log_scrape indentation in ai_handler.py

# Backup original file
cp /mnt/home2/mud/ai/ai_handler.py /mnt/home2/mud/ai/ai_handler.py.bak3

# Remove the misplaced log_scrape definition
sed -i '/async def log_scrape(self, url: str, data: Dict) -> None:/,+1d' /mnt/home2/mud/ai/ai_handler.py

# Insert log_scrape correctly indented after scrape_web
sed -i '/async def scrape_web(self, url: str) -> Optional\[Dict\]:/a\    async def log_scrape(self, url: str, data: Dict) -> None:\n        logger.info(f"Scraped website: {url}", extra={"level": "scraped"})' /mnt/home2/mud/ai/ai_handler.py

echo "Fixed log_scrape indentation in ai_handler.py"
