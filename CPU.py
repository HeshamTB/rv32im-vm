from myhdl import intbv, bin


class CPU:
    """
        In this class, we have the following components:
            1- Registers ( just a typical array, contains 32 slots. Each slot stores integers. )
            2- Fetch instructions
            3- Decode instructions
            4- Execute instructions -> using the ALU sub-class
    """

    # ALU Inner class
    class ALU:
        """
            A sub class that has a function for each major arithmetic and logic operation (e.g. ADD, SUB, SHIFT, etc).
            These major functions should be called from within the cpu, by the executioner function.
        """

        def __init__(self):
            self.func3 = 0
            self.func7 = 0
            self.rd = 0
            self.rs1 = 0
            self.rs2 = 0

        # TODO: check if ADD/SUB need special treatment in case of signed/unsigned
        def ADD(self, arg1, arg2):
            return arg1 + arg2

        def SUB(self, arg1, arg2):
            return self.ADD(arg1, -arg2)

        def OR(self, arg1, arg2):
            return arg1 | arg2

        def XOR(self, arg1, arg2):
            return arg1 ^ arg2

        def AND(self, arg1, arg2):
            return arg1 & arg2

        def SHIFT(self, arg1, arg2, dir='r', signed=False):  # needs testing
            if dir == "r":
                if signed:
                    return intbv(arg1 >> arg2).signed()  # arg1 must be signed number from the caller
                else:
                    return arg1 >> arg2  # arg1 is not signed number
            elif dir == "l":
                return arg1 << arg2

        def COMP(self, arg1: intbv, arg2: intbv, cond="e", signed=True):
            if cond == "e":
                return arg1 == arg2
            elif cond == "l":
                if not signed:
                    return arg1.unsigned() < arg2.unsigned()
                else:
                    return arg1 < arg2
            elif cond == "g":
                if not signed:
                    return arg1.unsigned() > arg2.unsigned()
                else:
                    return arg1 > arg2

        def MUL(self, arg1: intbv, arg2: intbv, sign='S'):  # I considered the notation (s)(u) to mean arg1 is signed, arg2 not signed
            if sign.capitalize() == 'SU':
                return arg1.signed() * arg2.unsigned()
            elif sign.capitalize() == 'U':
                return arg1.unsigned()*arg2.unsigned()
            elif sign.capitalize() == 'S':
                return arg1 * arg2
            else:
                print("Error: condition " + sign + " is not defined for MUL function")

        def DIV(self, arg1: intbv, arg2: intbv, signed=True):
            if not signed:
                return arg1.unsigned() / arg2.unsigned()
            return arg1/arg2

        def REM(self, arg1: intbv, arg2: intbv, signed=True):
            if not signed:
                arg1.unsigned() % arg2.unsigned()
            return arg1 % arg2

        # TODO: Think about the two functions commented below. If they serve no purpose anymore, delete them.
        # def exc_arithmetic(self, arg1, arg2, fn3, fn7=None, s=False, b=False):
        #     if fn3 == 0x0:  # ADD, SUB, MUL
        #         if fn7 == 0x01:
        #             return arg1*arg2
        #         elif fn7 == 0x00 or fn7 is None:
        #             return arg1+arg2
        #         elif fn7 == 0x20:
        #             return arg1-arg2
        #
        #     elif fn3 == 0x1:
        #         if fn7 == 0x01:  # MUL HIGH
        #             return arg1 * arg2  # Needs attention
        #
        #     elif fn3 == 0x2:
        #         if fn7 == 0x01:  # MUL HIGH (S)(U)
        #             return arg1 * arg2  # Needs attention
        #
        #     elif fn3 == 0x3:
        #         if fn7 == 0x01:  # MUL HIGH (U)
        #             return arg1 * arg2  # Needs attention
        #
        #     elif fn3 == 0x4:
        #         if fn7 == 0x01:
        #             return arg1/arg2
        #
        #     elif fn3 == 0x5:
        #         if fn7 == 0x01:  # DIV (U)
        #             return arg1 / arg2  # Needs Attention
        #
        #     elif fn3 == 0x6:
        #         if fn7 == 0x01:  # REMAINDER
        #             return arg1 % arg2
        #
        #     elif fn3 == 0x7:
        #         if fn7 == 0x01:  # REMAINDER (U)
        #             return arg1 % arg2  # Needs attention

        # def exc_logic(self, arg1, arg2, func3, func7, s=False, b=False):
        #     if func7 ==
    # End of ALU inner class

    # Constructor of CPU
    def __init__(self):
        """
            CPU constructor
            This initializes the registers and the ALU unit.
            Input: NONE
        """
        self.regs = [0 for i in range(32)]  # The Registers. Just a typical list
        self.alu_unit = self.ALU()  # The alu unit processes any possible arithmetic/logical operations for the cpu

    # Fetching Area:
    """
        Fetch the next instruction from the memory.
    """

    # Decoding:
    """
        Get the following:
            Opcode
            Rs1
            Rs2
            Rd
            func7
            func3
            imm if available ... etc
        and pass them to the executioner.
    """

    # Execution area:
    # TODO: This function will get replaced by many "Specialized" functions, for each format. (for example exc_R)
    def execution(self, opcode, rd, func3, rs1, rs2, func7, imm):
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
                3- If found, call the corresponding function
                4- Each instruction has a function to execute it
                5- Write back
        """

        #  Below lines for testing
        tst_regs = [0 for i in range(32)]
        opcode = int.to_bytes(0b0110011, 1, 'little')
        func3 = int.to_bytes(0b000, 1, 'little')
        func7 = int.to_bytes(0b0000000, 1, 'little')
        rd = int.to_bytes(0b00011, 1, 'little')
        rs1 = int.to_bytes(0b00100, 1, 'little')
        rs2 = int.to_bytes(0b00101, 1, 'little')
        #  End of testing area

        # TODO: Think if the following if statements have any use. Otherwise, delete them.
        if opcode == 0b0110011:  # R
            self.alu_unit.exc_arithmetic()
            self.alu_unit.exc_logic()
            pass
        elif opcode == 0b0010011:  # I
            self.alu_unit.exc_arithmetic()
            self.alu_unit.exc_logic()
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


        # Following dictionaries were for testing.
        # instructions_dictionary = {0b0110011:
        #                                [{'inst': 'add', 'func3': '000', 'func7': '0000000'},
        #                                 {'inst': 'sub', 'func3': '000', 'func7': '0100000'},
        #                                 {'inst': 'xor', 'func3': '100', 'func7': '0000000'},
        #                                 {'inst': 'or', 'func3': '110', 'func7': '0000000'},
        #                                 {'inst': 'and', 'func3': '111', 'func7': '0000000'},
        #                                 {'inst': 'sll', 'func3': '001', 'func7': '0000000'},
        #                                 {'inst': 'srl', 'func3': '101', 'func7': '0000000'},
        #                                 {'inst': 'sra', 'func3': '101', 'func7': '0100000'},
        #                                 {'inst': 'slt', 'func3': '010', 'func7': '0000000'},
        #                                 {'inst': 'sltu', 'func3': '011', 'func7': '0000000'}],
        #                            0b0010011: "I",
        #                            0b0000011: "L",
        #                            0b0100011: "S",
        #                            0b1100011: "B",
        #                            0b1101111: "J",
        #                            0b1100111: "Jalr",
        #                            0b0110111: "lui",
        #                            0b0010111: "auipc",
        #                            0b1110011: "syscalls"}
        # print()
        # instructions_dictionary = {0b0110011: {'func3': 0b000, 'func7': 0b0000000},
        #                            0b0010011: "I",
        #                            0b0000011: "L",
        #                            0b0100011: "S",
        #                            0b1100011: "B",
        #                            0b1101111: "J",
        #                            0b1100111: "Jalr",
        #                            0b0110111: "lui",
        #                            0b0010111: "auipc",
        #                            0b1110011: "syscalls"}

# Testing area:
x = CPU.ALU()
#x.exc_arithmetic(0,0)
y = 5
ar = bytearray(5)
ar[1] = 255
print(ar[1])
print(ar)


# Notes:
# We can use bytearray indices as numbers. for example if x is a bytearray, we can access like
# x[3] -> will return the fourth byte in the array. Just like normal arrays. it will be returned as integer.
# We can also manipulate it like integer or bits. It is acutally binary. we can do x[3] & 0b0001 or
# x[3] = y + 4 or any other operation, and it will be stored back as a byte.

# also note that we can use intbv for slicing
