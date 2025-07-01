import asyncio
import logging

logger = logging.getLogger("hipaa-medical-mcp")

async def call_local_llama(prompt):
    """Call local LLaMA model for AI responses"""
    try:
        process = await asyncio.create_subprocess_exec(
            "ollama", "run", "llama3.2:latest",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate(input=prompt.encode())
        
        if process.returncode != 0:
            raise Exception(f"LLaMA execution failed: {stderr.decode()}")
        
        return stdout.decode().strip()
        
    except Exception as e:
        logger.warning(f"Local LLaMA unavailable: {e}")
        return "LLaMA model is currently unavailable. Please try again later."