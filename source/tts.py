import asyncio, edge_tts, subprocess, os

VOICE = "en-AU-WilliamNeural"
LINES = [
    (1, 0.80, "Every science lesson says: look at the graph."),
    (2, 4.95, "For a blind student, that's where the lesson ends."),
    (3, 9.95, "GraphEar turns any spreadsheet into sound. Pitch is value, time is order."),
    (4, 15.95, "That spike is real — and now it's audible."),
    (5, 20.25, "Pitch is height. Rhythm is order. A second series pans left and right."),
    (6, 26.15, "Every insight arrives three ways: sound, plain language, and touch."),
    (7, 32.15, "Drop a CSV. Press play. Export the text and the tactile sheet."),
    (8, 37.45, "GraphEar. Hear your data."),
]

async def gen():
    for n, start, text in LINES:
        c = edge_tts.Communicate(text, VOICE, rate="-4%", pitch="-2Hz")
        await c.save(f"out/vo/line{n}.mp3")
asyncio.run(gen())

for n, start, text in LINES:
    subprocess.run(["ffmpeg","-y","-v","error","-i",f"out/vo/line{n}.mp3",
                    "-ar","44100","-ac","2",f"out/vo/line{n}.wav"], check=True)
print("generated", len(LINES), "lines")
