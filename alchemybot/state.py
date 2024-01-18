from typing import List, Optional
from alchemybot.substances import (
    Substance,
    full_substance,
    create_symbol,
    identify_copy,
)
from alchemybot.ai import get_embedding
import numpy as np


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))  # type: ignore


class GameState:
    def __init__(self, on_add_substance):
        self.substances = []
        self.on_add_substance = on_add_substance

    def has_symbol(self, symbol: str) -> bool:
        for substance in self.substances:
            if substance.symbol == symbol:
                return True
        return False

    async def ensure_symbol(
        self,
        symbol: str,
        name: str,
        description: str,
    ) -> str:
        used_symbols = []

        while self.has_symbol(symbol):
            used_symbols.append(symbol)
            symbol = await create_symbol(name, description, used_symbols)

        return symbol

    async def add_substance(self, substance: Substance):
        # Get the closest 5 substances
        with_distances = [
            (other, cosine_similarity(substance.embedding, other.embedding))
            for other in self.substances
        ]
        with_distances.sort(key=lambda x: x[1], reverse=True)
        with_distances = with_distances[:5]

        closest = [other for other, _ in with_distances]

        if await identify_copy(substance, closest):
            print(
                f"The substance {substance.name} is a copy of another substance and won't be added."
            )
            return

        substance.symbol = await self.ensure_symbol(
            substance.symbol, substance.name, substance.description
        )
        self.substances.append(substance)
        await self.on_add_substance(substance)

    async def search_substances(self, query: str) -> List[Substance]:
        # Get the closest 5 substances
        print(query)
        query_emb = await get_embedding(query)
        with_distances = [
            (other, cosine_similarity(query_emb, other.embedding))
            for other in self.substances
        ]
        with_distances.sort(key=lambda x: x[1], reverse=True)
        with_distances = with_distances[:5]

        closest = [other for other, _ in with_distances]

        return closest

    async def starter_substances(self):
        await self.add_substance(await full_substance("water"))
        await self.add_substance(await full_substance("fire"))
        await self.add_substance(await full_substance("earth"))
        await self.add_substance(await full_substance("air"))
        pass
