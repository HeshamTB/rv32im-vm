
class Memory:
    """
    Object class of a Random access memory. Byte addressable.
    Args:
        size: size of memory
    """
    def __init__(self, size: int):
        self.mem = [bytes() for i in range(size)]
    
    def getSize(self) -> int:
        """
        Returns the size or number of bytes of the memory module.
        """
        return len(self.mem)
    
    def write(self, address: int, value: bytes):
        """
        Write the passed byte to address
        args:
            address: location to write to.
            value: value as bytes object
        """
        self.mem[address] = value
    
    def read(self, address: int) -> bytes:
        """
        Read address as byte
        """
        return self.mem[address]

    def readHalfWord(self, address: int) -> bytes:
        return self.mem[address] + self.mem[address+1]
    
    def readWord(self, address: int) -> bytes:
        return self.mem[address] + self.mem[address+1] + self.mem[address+2] + self.mem[address+3]

    def readAsInt(self, address: int) -> int:
        # TODO check if valid address
        val = int.from_bytes(self.mem[address], 'little')
        return val
    
    def dump(self) -> str:
        import os
        values = list()
        for i, val in enumerate(self.mem):
            values.append(hex(int.from_bytes(val, 'little')))

        dum = str()
        for i, val in enumerate(values):
           dum = dum + hex(i) +' '+ val + os.linesep
        return dum

if __name__ == '__main__':
    x = Memory(50)
    x.write(0x22, int(22).to_bytes(1,'little'))
    print(x.dump())