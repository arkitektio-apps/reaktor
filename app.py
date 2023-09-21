from arkitekt import register
import time
import asyncio

@register
async def count_down(number: int):
    """Count Down
    
    Count down from a number to 0.
    """

    for i in range(number, 0, -1):
        print(i)
        await asyncio.sleep(1)
        yield i

