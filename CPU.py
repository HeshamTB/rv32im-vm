from myhdl import intbv, bin
"""
    In this file, we have the following sections:
        1- Registers initializing
        2- Fetch instructions
        3- Decode instructions
        4- Execute instructions
"""


# Registers:
#   An array

# Fetching:
#   Fetch from memory the instruction that program counter is pointing to.

# Decoding:
#   Get the following:
#   Opcode
#   Rs1
#   Rs2
#   Rd
#   func7
#   func3

# Execution:

def execute(opcode, rd, func3, rs1, rs2, func7):
    """
        Requirements:
            1- opcode (Used to know the format type)
            2- func3-func7-rd-rs1-rs2

        Bit slicing: (below are inclusive start- inclusive end)
        opcode: 0-6
        rd: 7-11
        func3: 12-14
        rs1: 15-19
        rs2: 20-24
        func7: 25-31

        Execution
            1- All instructions dictionary
            2- Loop over opcode
            3- If found, .....
            4- Each instruction has a function to execute it
            5- Write back
    """
    tst_regs = [0 for i in range(32)]
    opcode = int.to_bytes(0b0110011, 1, 'little')
    func3 = int.to_bytes(0b000, 1, 'little')
    func7 = int.to_bytes(0b0000000, 1, 'little')
    rd = int.to_bytes(0b00011, 1, 'little')
    rs1 = int.to_bytes(0b00100, 1, 'little')
    rs2 = int.to_bytes(0b00101, 1, 'little')

    if opcode == 0b0110011:  # R

        pass
    elif opcode == 0b0010011:  # I
        pass
    elif opcode == 0b0000011:  # L
        pass
    elif opcode == 0b0100011:  # S
        pass
    elif opcode == 0b1100011:  # B
        pass
    elif opcode == 0b1101111:  # J
        pass
    elif opcode == 0b1100111:  # jalr
        pass
    elif opcode == 0b0110111:  # lui
        pass
    elif opcode == 0b0010111:  # auipc
        pass
    elif opcode == 0b1110011:  # syscalls
        pass

    instructions_dictionary = {0b0110011:
                         [{'inst': 'add', 'func3': '000',  'func7': '0000000'},
                          {'inst': 'sub', 'func3': '000',  'func7': '0100000'},
                          {'inst': 'xor', 'func3': '100',  'func7': '0000000'},
                          {'inst': 'or',  'func3': '110',  'func7': '0000000'},
                          {'inst': 'and', 'func3': '111',  'func7': '0000000'},
                          {'inst': 'sll', 'func3': '001',  'func7': '0000000'},
                          {'inst': 'srl', 'func3': '101',  'func7': '0000000'},
                          {'inst': 'sra', 'func3': '101',  'func7': '0100000'},
                          {'inst': 'slt', 'func3': '010',  'func7': '0000000'},
                          {'inst': 'sltu', 'func3': '011', 'func7': '0000000'}],
                               0b0010011: "I",
                               0b0000011: "L",
                               0b0100011: "S",
                               0b1100011: "B",
                               0b1101111: "J",
                               0b1100111: "Jalr",
                               0b0110111: "lui",
                               0b0010111: "auipc",
                               0b1110011: "syscalls"}
    print()
    instructions_dictionary = {0b0110011: {'func3': 0b000, 'func7': 0b0000000},
                               0b0010011: "I",
                               0b0000011: "L",
                               0b0100011: "S",
                               0b1100011: "B",
                               0b1101111: "J",
                               0b1100111: "Jalr",
                               0b0110111: "lui",
                               0b0010111: "auipc",
                               0b1110011: "syscalls"}










