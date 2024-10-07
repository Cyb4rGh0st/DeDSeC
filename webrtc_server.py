import asyncio
from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.signaling import TcpSocketSignaling, BYE

# Klasa do zarządzania dźwiękiem
class AudioBlackhole(MediaStreamTrack):
    kind = "audio"

    def __init__(self):
        super().__init__()  # Poprawnie wywołaj konstruktor

    async def recv(self):
        return None  # Zwracaj None w przypadku braku danych

# Klasa do zarządzania wideo
class VideoBlackhole(MediaStreamTrack):
    kind = "video"

    def __init__(self):
        super().__init__()  # Poprawnie wywołaj konstruktor

    async def recv(self):
        return None  # Zwracaj None w przypadku braku danych

# Funkcja do uruchomienia WebRTC
async def run(pc, signaling):
    await signaling.connect()

    if signaling.is_initiator:
        offer = await pc.createOffer()
        await pc.setLocalDescription(offer)
        await signaling.send(pc.localDescription)

    while True:
        obj = await signaling.receive()

        if isinstance(obj, RTCSessionDescription):
            await pc.setRemoteDescription(obj)
            if obj.type == "offer":
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await signaling.send(pc.localDescription)
        elif obj is BYE:
            print("Połączenie zakończone")
            break

# Konfiguracja WebRTC
pc = RTCPeerConnection()

# Dodajemy tracki
pc.addTrack(AudioBlackhole())
pc.addTrack(VideoBlackhole())

# TCP Signaling (na porcie 9999)
signaling = TcpSocketSignaling("localhost", 9999)

# Uruchomienie połączenia
asyncio.run(run(pc, signaling))