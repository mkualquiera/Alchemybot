import asyncio
from dataclasses import dataclass
from typing import List, Optional, Tuple
from alchemybot.prompts import PROMPTS
from alchemybot.ai import get_json_data, get_embedding


@dataclass
class Substance:
    name: str
    description: str
    symbol: str
    pictogram: str
    embedding: List[float]


async def describe_substance(name: str) -> str:
    """Returns a description of the substance."""

    # get the prompt from the PROMPTS dict
    prompt = PROMPTS["describe_substance"]

    # get the json data from the AI
    result = await get_json_data(prompt, f"Substance name: {name}")

    # return the description
    return result["description"]


async def create_symbol(
    name: str, description: str, existing_symbols: Optional[List[str]] = None
) -> str:
    """Returns a possible symbol for the substance."""

    # get the prompt from the PROMPTS dict
    prompt = PROMPTS["create_symbol"]

    user_prompt = ""
    if existing_symbols is not None and len(existing_symbols) > 0:
        user_prompt = (
            f"The following symbols already exist and CANNOT be "
            f"used: {', '.join(existing_symbols)}"
        )

    user_prompt += f"\nSubstance name: {name}\nDescription: {description}"

    # get the json data from the AI
    result = await get_json_data(prompt, user_prompt, model="gpt-3.5-turbo")

    # return the symbol
    return result["symbol"]


async def create_pictogram(name: str, description: str) -> str:
    """Returns the description of a pictogram for the substance."""

    # get the prompt from the PROMPTS dict
    prompt = PROMPTS["create_pictogram"]

    user_prompt = f"Substance name: {name}\nDescription: {description}"

    # get the json data from the AI
    result = await get_json_data(prompt, user_prompt)

    return result["pictogram"]


async def describe_alchemical_process(
    image_url: str, substances: List[Substance]
) -> Tuple[str, str]:
    """Returns a description of the alchemical process."""

    # get the prompt from the PROMPTS dict
    prompt = PROMPTS["describe_alchemical_process"]

    # user_prompt = [
    #    f"{substance.name}: {substance.pictogram}" for substance in substances
    # ]

    user_prompt = "PICTOGRAMS: "

    for substance in substances:
        user_prompt += f"\n{substance.name}: {substance.pictogram}"

    user_prompt += f"\n"

    print(user_prompt)

    # get the json data from the AI
    result = await get_json_data(
        prompt,
        user_prompt=user_prompt,
        image_url=image_url,
        model="gpt-4-vision-preview",
    )

    # return the description
    return result["process"], result["problems"]


async def perform_alchemical_process(
    substances: List[Substance], process: str, problems: Optional[str]
) -> List[str]:
    """Returns a list of substances created by the alchemical process."""

    # get the prompt from the PROMPTS dict
    prompt = PROMPTS["perform_alchemical_process"]

    user_prompt = [
        f"{substance.name}: {substance.description}" for substance in substances
    ]

    user_prompt = "DESCRIPTIONS: " + "\n".join(user_prompt)

    user_prompt += f"\nProcess to follow: {process}"

    if problems is not None:
        user_prompt += f"\nProblems with this process: {problems}"
    else:
        user_prompt += "\nNo problems were found with this process."

    # get the json data from the AI
    result = await get_json_data(prompt, user_prompt)

    # return the list of substances
    return result["results"]


async def full_substance(name: str) -> Substance:
    """Returns a full substance from the name."""

    description = await describe_substance(name)

    # Create tasks to run in parallel
    symbol_task = create_symbol(name, description)
    pictogram_task = create_pictogram(name, description)

    # Run tasks in parallel
    symbol, pictogram = await asyncio.gather(symbol_task, pictogram_task)

    # Compute the embedding for the substance
    embedding = await get_embedding(f"The substance named {name}: {description}")

    return Substance(name, description, symbol, pictogram, embedding)


async def identify_copy(substance: Substance, others: List[Substance]) -> bool:
    """Returns true if the substance is a copy of one of the others."""

    # get the prompt from the PROMPTS dict
    prompt = PROMPTS["substance_copy_identifier"]

    user_prompt = "Closest substances: "

    for other in others:
        user_prompt += f"\n{other.name}: {other.description}"

    user_prompt += f"\nSubstance to check: {substance.name}: {substance.description}"

    # get the json data from the AI
    result = await get_json_data(prompt, user_prompt)

    # return the result
    return result["is_copy"]
