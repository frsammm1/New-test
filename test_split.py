import asyncio
from io import BytesIO

class MockStream:
    def __init__(self, data):
        self.data = data
        self.pos = 0

    async def read(self, size=-1):
        if self.pos >= len(self.data):
            return b""
        if size == -1:
            chunk = self.data[self.pos:]
            self.pos += len(chunk)
            return chunk
        chunk = self.data[self.pos:self.pos+size]
        self.pos += len(chunk)
        return chunk

    async def close(self):
        print("MockStream closed")

class SplitFile:
    def __init__(self, stream, max_size):
        self.stream = stream
        self.max_size = max_size
        self.current_pos = 0
        self.closed = False

    async def read(self, size=-1):
        if self.closed:
            return b""

        remaining = self.max_size - self.current_pos
        if remaining <= 0:
            return b""

        if size == -1 or size > remaining:
            size = remaining

        chunk = await self.stream.read(size)
        if not chunk:
            return b""

        self.current_pos += len(chunk)
        return chunk

    async def close(self):
        self.closed = True
        # Do not close parent stream

async def main():
    # 20 bytes of data
    data = b"01234567890123456789"
    source = MockStream(data)

    # Split into 2 parts of 10 bytes
    part1 = SplitFile(source, 10)
    read1 = await part1.read(15) # Ask for 15, should get 10
    print(f"Part 1: {read1} (Len: {len(read1)})")

    part2 = SplitFile(source, 10)
    read2 = await part2.read(15) # Ask for 15, should get remaining 10
    print(f"Part 2: {read2} (Len: {len(read2)})")

    # Verify exact split
    assert read1 == b"0123456789"
    assert read2 == b"0123456789"
    print("Split logic verified")

asyncio.run(main())
