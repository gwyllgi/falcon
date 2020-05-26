import discord

import settings as discord_settings

client = discord.Client()


@client.event
async def on_message(message):
    # if bot send message then dont send anything
    if message.author == client.user:
        return
    if message.content.lower() == discord_settings.CLIENT_INPUT_GREETING:
        await message.channel.send(discord_settings.CLIENT_OUTPUT_GREETING)

if __name__ == '__main__':
    client.run(discord_settings.TOKEN)
