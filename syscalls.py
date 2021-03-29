# Implementaion of syscall layer in rv32im-vm
# Parsing method and exec methods

from mem import Memory
from myhdl import intbv
import sys

def handle(regs: list[intbv], mem: Memory):
    # Read reg values
    # a7 req/funct
    # a1, a2 from to if print
    # stdin, stdout

    if regs[17].unsigned() == 64:
        # Print to console
        data = getTextFromMem(mem,regs[11].unsigned(), regs[12].unsigned())
        stream = regs[10].unsigned()
        _sys_print(stream, data)
    elif regs[17] == 0:
        exit_val = regs[10] # Exit code in a0, x10. could be signed
        _sys_exit(exit_val)
    else:
        # Unimplemented req
        pass

def _sys_print(data, stream: int = 0):
    # stdin 0, stdout 1, stderr 2
    if stream == 1:
        print(data, file=sys.stdout)
    elif stream == 2:
        print(data, file=sys.stderr)
    else:
        pass # Exception?

def _sys_exit(code: int):
    pass

def _getTextFromMem(mem: Memory, start_add, length):
    val = bytes()
    for i in range(length):
        address = start_add + i  # Start add + inc. byte by byte
        val += mem.read(address)
    if val.isascii():
        return val.decode('ascii')
    elif val.isnumeric():
        return int.from_bytes(val, 'little')
