import asyncio
# import sys
from src.client.hipaa_client import HIPAAMedicalClient

async def main():
    client = HIPAAMedicalClient()
    await client.run()

if __name__ == "__main__":
    asyncio.run(main())