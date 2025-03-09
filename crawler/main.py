# main.py
# docker exec -it crawler python /app/main.py

import asyncio

print("Main script engegat...")

# Lògica del crawler (afegir la resta del codi de processament aquí)
async def run_crawler():
    # Aquí escriure la lògica per navegar i recollir dades
    pass

if __name__ == "__main__":
    # Assegurar-se que la funció només es cridi una vegada
    asyncio.run(run_crawler())
