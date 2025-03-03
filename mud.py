# mud.py
# ... (keep existing imports)

async def handle_client(reader, writer):
    term = TermHandler()
    network = NetworkHandler(None)
    login_handler = LoginHandler()
    login_handler.term_handler = term
    login_handler.network_handler = network
    
    try:
        player = await login_handler.handle_login(reader, writer)
        if not player:
            writer.close()
            return
    except Exception as e:
        writer.write(term.format_output(f"{COLORS['error']}Login failed: {str(e)}{COLORS['reset']}").encode())
        writer.close()
        return
    
    combat = CombatHandler(player)
    ritual = RitualHandler(player)
    inventory = InventoryHandler(player)
    soul = SoulHandler(player)
    
    players[writer] = {
        "player": player, "room": rooms["waterdeep/market"], "term": term, "network": network,
        "combat": combat, "ritual": ritual, "inventory": inventory, "soul": soul
    }
    
    # Optional AI interaction
    if player.deity:
        ai_handler = AIHandler()
        await ai_handler.load_agent(player.deity, player.deity, "maintainer")
        await ai_handler.assign_task(player.deity, "maintain")
    
    writer.write(term.format_output(f"{COLORS['info']}Welcome to Faerûn, {player.name}! Type 'help' for commands.{COLORS['reset']}").encode())
    await writer.drain()
    
    # ... (rest unchanged)
