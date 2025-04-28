# crawler_rag/main.py
# docker exec -it crawler python /app/main.py

import asyncio

print("Main script engegat...")

# Lògica del crawler
# Ara, funció buida 
async def stay_alive():
    try:
        while True:
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        print("Sortint...")


if __name__ == "__main__":
    # Ens assegurem q funció només es cridi una vegada
    asyncio.run(stay_alive())