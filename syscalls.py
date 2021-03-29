# Implementaion of syscall layer in rv32im-vm
# Parsing method and exec methods

from mem import Memory
from myhdl import intbv
import sys

_function = 17
_address = 11
_length = 12
_code = 10

_syscall_exit = 93
_syscall_print = 64

_stdout = 1
_stderr = 2

def handle(regs: list[intbv], mem: Memory):
    # Read reg values
    # a7 req/funct
    # a1, a2 from to if print
    # stdin, stdout

    if regs[_function].unsigned() == _syscall_print:
        # Print to console
        data = _getTextFromMem(mem, regs[_address].unsigned(), regs[_length].unsigned())
        stream = regs[_code].unsigned()
        _sys_print(stream, data)
    elif regs[_function] == _syscall_exit:
        exit_val = regs[_code] # Exit code in a0, x10. could be signed
        _sys_exit(int(exit_val))
    else:
        # Unimplemented req
        pass

def _sys_print(data, stream: int = 0):
    # stdin 0, stdout 1, stderr 2
    if stream == _stdout:
        print(data, file=sys.stdout)
    elif stream == _stderr:
        print(data, file=sys.stderr)
    else:
        pass # Exception?

def _sys_exit(code: int):
    exit(code)

def _getTextFromMem(mem: Memory, start_add, length):
    val = bytes()
    for i in range(length):
        address = start_add + i  # Start add + inc. byte by byte
        val += mem.read(address)
    if val.isascii():
        return val.decode('ascii')
    else:
        return int.from_bytes(val, 'little')
