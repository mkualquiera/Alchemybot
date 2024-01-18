from dotenv import load_dotenv

load_dotenv()

import os
import openai
import pickle
import discord
from alchemybot.substances import (
    describe_substance,
    create_symbol,
    create_pictogram,
    describe_alchemical_process,
    perform_alchemical_process,
    full_substance,
)
from alchemybot.state import GameState

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = os.getenv("GUILD_ID")
CHANNEL_ID = os.getenv("CHANNEL_ID")


if DISCORD_TOKEN is None:
    raise Exception("Discord token not found in environment variables")
# set api key
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


async def on_add_substance(substance):
    # save state
    with open("state.pickle", "wb") as f:
        pickle.dump(state, f)

    message = (
        f"# {substance.symbol}\n**{substance.name}**\n"
        f"{substance.description}\n"
        f"_{substance.pictogram}_"
    )
    await channel.send(message)  # type: ignore


new_state = False
if not os.path.exists("state.pickle"):
    state = GameState(on_add_substance)
    new_state = True
else:
    with open("state.pickle", "rb") as f:
        state = pickle.load(f)

    print("Loaded state from file")

    state.on_add_substance = on_add_substance


@client.event
async def on_ready():
    global channel
    # Get the guild and channel
    guild = client.get_guild(int(GUILD_ID))  # type: ignore
    channel = guild.get_channel(int(CHANNEL_ID))  # type: ignore
    if new_state:
        await state.starter_substances()
    print("Alchemybot is ready!")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Describe a substance
    # if message.content.startswith("!describe"):
    #    substance_name = message.content.split(" ", 1)[1]
    #    description = await describe_substance(substance_name)
    #    await message.channel.send(description)
    #    symbol = await create_symbol(substance_name, description)
    #    await message.channel.send(symbol)
    #    pictogram = await create_pictogram(substance_name, description)
    #    await message.channel.send(pictogram)

    ## Take an image
    if message.content.startswith("!process"):
        image_url = message.attachments[0].url

        # Get the list of substances
        substances = []
        elements = message.content.split(" ")[1:]
        for element in elements:
            for substance in state.substances:
                if substance.symbol == element:
                    substances.append(substance)
                    break
            else:
                await message.channel.send(
                    f"Substance {element} not found. Please try again."
                )
                return

        description, problems = await describe_alchemical_process(image_url, substances)

        if problems is not None:
            # await message.channel.send(problems)
            # respond to the user with the problems
            await message.reply(problems)

        await message.reply(description)

        results = await perform_alchemical_process(substances, description, problems)

        if len(results) == 0:
            await message.reply("The process failed.")
            return

        for result in results:
            await state.add_substance(await full_substance(result))

    if message.content.startswith("!substances"):
        result = ""
        counter = 0
        for substance in state.substances:
            result += (
                f"**{substance.symbol}** - {substance.name}: {substance.pictogram}\n"
            )
            counter += 1
            if counter >= 10:
                await message.channel.send(result)
                result = ""
                counter = 0

        if result != "":
            await message.channel.send(result)

    if message.content.startswith("!ssearch"):
        query = message.content[len("!ssearch") :].strip()
        results = await state.search_substances(query)

        result = ""
        counter = 0

        for substance in results:
            result += f"**{substance.symbol}** - {substance.name}: {substance.description} - _{substance.pictogram}_\n"
            counter += 1
            if counter >= 10:
                await message.channel.send(result)
                result = ""
                counter = 0

        if result != "":
            await message.channel.send(result)


client.run(DISCORD_TOKEN)
