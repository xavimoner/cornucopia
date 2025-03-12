# main.py
# docker exec -it crawler python /app/main.py

import asyncio

print("Main script engegat...")

# Lògica del crawler 
async def run_crawler():
    # lògica per navegar i recollir dades
    pass

if __name__ == "__main__":
    # Ens assegurem q funció només es cridi una vegada
    asyncio.run(run_crawler())
