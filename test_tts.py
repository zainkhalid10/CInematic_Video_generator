import asyncio
import edge_tts

async def main():
    try:
        c = edge_tts.Communicate("Hello world", "en-US-GuyNeural")
        await c.save("test.wav")
        print("Success")
    except Exception as e:
        print("Error:", e)

asyncio.run(main())
