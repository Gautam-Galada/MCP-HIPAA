import asyncio
from src.server.hipaa_server import HIPAAMedicalServer

async def main():
    server = HIPAAMedicalServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())