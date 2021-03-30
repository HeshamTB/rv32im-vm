from myhdl import intbv, bin
from mem import Memory
import syscalls


class CPU:
    """
        In this class, we have the following components/sections:
            1- Registers (just a typical array, contains 32 slots. Each slot stores integers or intbv, not decided yet)
            2- Fetch instructions
            3- Decode instructions
            4- Execute instructions
    """

    # Constructor of CPU
    def __init__(self, ram: Memory):
        """
            CPU constructor
            This initializes the registers
            Input: NONE
        """
        self.regs = [intbv(0)[32:0] for i in range(32)]  # The Registers. Just a typical list
        self.pc = 0
        self.ram = ram
        self.jump_flag = False

    # =========== Fetching Area =========== #
    """
        Fetch the next instruction from the memory.
    """
    def fetch(self):
        self.jump_flag = False
        inst = self.ram.readWord(self.pc)
        inst = int.from_bytes(inst, byteorder='little')
        self.execution1(intbv(inst)[32:])

    # =========== Decoding Area =========== #
    """
        Get the following:
            Opcode
            Rs1
            Rs2
            Rd
            func7
            func3
            imm if available ... etc
        and pass the suitable arguments to the appropriate execution function, based on opcode, func3 and func7.
    """

    # =========== Execution Area =========== #
    # TODO: 1-Check if ADD/SUB need special treatment in case of signed/unsigned
    # TODO: 2-Check if we need some standard here, like return type or type of inputs.
    # TODO: 3-Currently we use ADD, SUB, SHIFT etc in other places. Think if eliminating this is useful or the opposite
    # ------------------------------------------- Basic instructions ------------------------------------------- #
    # ------ These return, but don't update registers. updating regs is caller responsibility in this case ------ #
    def ADD(self, arg1: intbv, arg2: intbv, rd: intbv) -> int:
        self.regs[rd] = intbv(arg1 + arg2)[32:]
        return arg1 + arg2

    def SUB(self, arg1: intbv, arg2: intbv, rd: intbv) -> int:
        return self.ADD(arg1, -arg2, rd)

    def OR(self, arg1, arg2, rd):
        self.regs[rd] = intbv(arg1 | arg2)[32:]
        return arg1 | arg2

    def XOR(self, arg1, arg2, rd):
        self.regs[rd] = intbv(arg1 ^ arg2)[32:]
        return arg1 ^ arg2

    def AND(self, arg1, arg2, rd):
        self.regs[rd] = intbv(arg1 & arg2)[32:]
        return arg1 & arg2

    def SHIFT(self, arg1: intbv, arg2: intbv, rd, dir='r', signed=False):  # needs testing
        """
        Shifts arg1 by amount of arg2
        Args:
            arg1: Number to be shifted
            arg2: Shift amount
            dir: direction of shift. By default is r. Set to l for shift left
            signed: Boolean flag for sign. By default is False. Set to True to enable sign extension
        Returns: arg1 shifted arg2 positions in dir direction
        """
        if dir == "r":
            if signed:
                self.regs[rd] = intbv(arg1.signed() >> arg2.signed())[32:]
                return arg1.signed() >> arg2.signed()
            else:
                self.regs[rd] = intbv(arg1 >> arg2)[32:]
                return arg1 >> arg2  # arg1 is not signed number
        elif dir == "l":
            self.regs[rd] = intbv(arg1 << arg2)[32:]
            return arg1 << arg2

    def COMPARE(self, arg1: intbv, arg2: intbv, rd, cond="e", signed=True):
        """
        Comapre arg1 and arg2.
        Args:
            arg1: first argument
            arg2: second argument
            cond: comparison condition. e for equal, l for less, and g for greater, le for <=, ge for >=.
            signed: Boolean flag for sign. By default is True. Set to False in case inputs are unsigned
        Returns: Boolean. indicates whether comparison result is true or false
        """
        if signed:  # Check the sign
            arg1 = arg1.signed()
            arg2 = arg2.signed()
        # Check the conditions
        if cond == "e":
            self.regs[rd] = intbv(arg1 == arg2)[32:]
            return arg1 == arg2
        elif cond == "l":
            self.regs[rd] = intbv(arg1 < arg2)[32:]
            return arg1 < arg2
        elif cond == "g":
            self.regs[rd] = intbv(arg1 > arg2)[32:]
            return arg1 > arg2
        elif cond == "le":
            self.regs[rd] = intbv(arg1 <= arg2)[32:]
        elif cond == "ge":
            self.regs[rd] = intbv(arg1 >= arg2)[32:]

    def MUL(self, arg1: intbv, arg2: intbv, rd, sign='S'):
        # I considered the notation (s)(u) to mean arg1 is signed, arg2 not signed
        if sign.capitalize() == 'SU':
            self.regs[rd] = intbv(arg1.signed() * arg2.unsigned())[32:]
            return arg1.signed() * arg2.unsigned()
        elif sign.capitalize() == 'U':
            self.regs[rd] = intbv(arg1 * arg2)[32:]
            return arg1 * arg2
        elif sign.capitalize() == 'S':
            self.regs[rd] = intbv(arg1.signed() * arg2.signed())[32:]
            return arg1.signed() * arg2.signed()
        else:
            print("Error: condition " + sign + " is not defined for MUL function")

    def DIV(self, arg1: intbv, arg2: intbv, rd, signed=True):
        if signed:
            self.regs[rd] = intbv(arg1.signed() // arg2.signed())[32:]
            return arg1.signed() // arg2.signed()
        self.regs[rd] = intbv(arg1 // arg2)[32:]
        return arg1 // arg2

    def REM(self, arg1: intbv, arg2: intbv, rd, signed=True):
        if signed:
            self.regs[rd] = intbv(arg1.signed() % arg2.signed())[32:]
            return arg1.signed() % arg2.signed()
        self.regs[rd] = intbv(arg1 % arg2)[32:]
        return arg1 % arg2

    # -------------------------- instructions of load -------------------------- #
    def LOAD(self, rd, rs1, imm: intbv, width=1, signed=True):
        """
        Executes load instructions.
        Load the value of memory address [ register rs1+imm value(offset) ] into register rd
        Args:
            rd: destination register
            rs1: source register
            imm: immediate value, represents offset
            width: number of bytes. can be 1, 2, or 4 for byte, half word, or word
            signed: boolean flag. Set to True by default. Set to False to enable unsigned immediate
        Returns: None
        """
        # These instructions take the form lb rd, imm(rs1)
        if signed:
            imm = imm.signed()
        src = intbv(self.regs[rs1])[32:0]
        target_address = src + imm
        loaded_bytes = None
        if width == 1:
            loaded_bytes = self.ram.read(target_address)
        elif width == 2:
            loaded_bytes = self.ram.readHalfWord(target_address)
        elif width == 4:
            loaded_bytes = self.ram.readWord(target_address)
        else:
            print("Error: please enter valid load width")
            exit(0)
        # Store the loaded byte as an integer in the destination reg
        self.regs[rd] = intbv(int.from_bytes(loaded_bytes, 'little')).signed()[32:]  # TODO: check sign extension

    # -------------------------- instructions of store -------------------------- #
    def STORE(self, rs1, rs2, imm: intbv, width=1):
        """
        Executes store instructions.
        Store the value found in rs2 into memory location stored in rs1+immediate(offset)
        Args:
            rs1: initial memory location
            rs2: register holding the value we want to store
            imm: immediate value, represents offset
            width: number of bytes. Can be 1, 2, or 4
        Returns: None
        """
        if width > 4:
            print("Error, maximum width is 4")

        src1 = intbv(self.regs[rs1])[32:0]
        print(self.regs[rs2])
        #print(width)
        src2 = int(intbv(self.regs[rs2])[8*width:0]).to_bytes(width, 'little')
        target_address = imm + src1
        print('src1 {} src2 {} target_add {}'.format(src1, src2, target_address))
        #print(target_address)
        # Loop, each time store one byte from src2 in the memory.

        for i in range(width):
            store_byte = src2[i].to_bytes(1, 'little')
            self.ram.write(target_address + i, store_byte)

    # -------------------------- Branch Instructions -------------------------- #
    def BRANCH(self, rs1, rs2, imm: intbv, cond='e', signed=True):
        """
        Execute branching instructions based on comparison conditions of two values
        Args:
            rs1: register source 1
            rs2: register source 2
            imm: immediate value
            cond: e for rs1==rs2, ne for !=, lt for <, ge for >=
            signed: boolean flag. True by default. Set to false to enable unsigned branch
        Returns:
        """
        val1 = intbv(self.regs[rs1])[32:0]
        val2 = intbv(self.regs[rs2])[32:0]
        res = False
        if signed:
            val1 = val1.signed()
            val2 = val2.signed()
        if cond == 'e':
            res = val1 == val2
        elif cond == 'ne':
            res = not (val1 == val2)
        elif cond == 'lt':
            res = val1 < val2
        elif cond == 'ge':
            res = val1 >= val2
        else:
            print("Error: Please enter valid comparison condition")

        if res:
            self.jump_flag = True
            self.pc = self.pc + int(imm.signed())

    # -------------------------- Jump instructions -------------------------- #
    def JAL(self, rd, imm: intbv):
        """
        Jump by increasing pc by amount of imm. Save return address in rd
        Args:
            rd: saves return address
            imm: immediate value. The pc will be incremented by this amount * 2
        Returns:
        """
        # First, shift the immediate to left once to multiply by 2
        imm = intbv(imm).signed()[21:0]  # TODO: check sign extension
        self.regs[rd] = intbv(self.pc + 4)[32:0]  # Save return address in rd
        self.jump_flag = True
        self.pc += imm  # jump

    def JALR(self, rd, rs1, imm: intbv):
        """
        Jump to address stored in rs1 + imm (immediate serves as offset, usually 0)
        Args:
            rd: saves return address
            rs1: contains the address to jump to
            imm: immediate value, serves as offset. Usually 0
        Returns: None
        """
        self.regs[rd] = intbv(self.pc + 4)[32:0]
        self.jump_flag = True
        self.pc = self.regs[rs1] + imm

    # -------------------------- Instructions with large immediate -------------------------- #
    def LUI(self, rd, imm: intbv):
        """
        Loads value of imm into upper 20 bits of rd register
        Args:
            rd: holds the immediate shifted 12 bits left
            imm: the value to be loaded
        Returns: None
        """
        if imm.max != 1048576:
            print('Error: Immediate passed to LUI is not 20 bits intbv')
            exit(0)
        imm = imm << 12
        self.regs[rd] = intbv(imm)[32:0]

    def AUIPC(self, rd, imm: intbv):
        """
        Adds immediate to pc's top 20 bits.
        Args:
            rd: stores (PC + imm<<12)
            imm: immediate value to be loaded
        Returns: None
        """
        if imm.max != 1048576:
            print('Error: Immediate passed to LUI is not 20 bits intbv')
            exit(0)
        imm = imm << 12
        self.regs[rd] = intbv(self.pc + imm)[32:0]

    # -------------------------- System calls -------------------------- #
    # TODO: Implement system calls.
    def ecall(self):
        syscalls.handle(self.regs, self.ram)

    def ebreak(self):
        pass

        # TODO: Following function was to be replaced by many functions, for each format (for example exc_R) ...
        #  ... but I decided to change that structure a bit and made functions for each major operation.
        #  this function now serves no purpose but its content can be used somewhere else. Consider deleting it later.

        #  Below lines for testing
        tst_regs = [0 for i in range(32)]
        opcode = int.to_bytes(0b0110011, 1, 'little')
        func3 = int.to_bytes(0b000, 1, 'little')
        func7 = int.to_bytes(0b0000000, 1, 'little')
        rd = int.to_bytes(0b00011, 1, 'little')
        rs1 = int.to_bytes(0b00100, 1, 'little')
        rs2 = int.to_bytes(0b00101, 1, 'little')
        #  End of testing area

    def execution1(self, memory_snippet):
        # ----------------------------- test -----------------------------#
        data_holder = memory_snippet
        rd = 0b0
        rs1 = 0b0
        rs2 = 0b0
        funct3 = 0b0
        funct7 = 0b0
        imm = 0b0
        imm1 = 0b0
        imm2 = 0b0

        key_opcodes = [0b0110011, 0b0010011, 0b0000011, 0b1100111, 0b1110011, 0b0100011, 0b1100011, 0b0110111,
                       0b0010111,
                       0b1101111]  # opcode for R I S B U J types.

        type_t = ''

        for i in range(len(key_opcodes)):
            if data_holder[7:0] == key_opcodes[i]:
                #print('match found')

                if i == 0:
                    print('Type is: ', 'R')
                    type_t = 'R'
                if i == 1:
                    print('Type is: ', 'I')
                    type_t = 'I1'
                if i == 2:
                    print('Type is: ', 'I')
                    type_t = 'I2'
                if i == 3:
                    print('Type is: ', 'I')
                    type_t = 'I3'
                if i == 4:
                    print('Type is: ', 'I')
                    type_t = 'I4'
                if i == 5:
                    print('Type is: ', 'S')
                    type_t = 'S'
                if i == 6:
                    print('Type is: ', 'B')
                    type_t = 'B'
                if i == 7:
                    print('Type is: ', 'U')
                    type_t = 'U1'
                if i == 8:
                    print('Type is: ', 'U')
                    type_t = 'U2'
                if i == 9:
                    print('Type is: ', 'J')
                    type_t = 'J'

        # ------------ R type execution section ------------#
        if type_t == 'R':
            rd = data_holder[12:7]
            rs1 = data_holder[20:15]
            rs2 = data_holder[24:20]
            funct3 = data_holder[15:12]
            funct7 = data_holder[32:25]
            print("Type R: func7: " + str(funct7) + "\t func3: "+ str(funct3) + "\t rs1: " + str(rs1) + "\t rs2: " + str(rs2)  +"\t rd: "+ str(rd))
            # look for the correct instruction via func3 and func7
            if funct3 == 0b000:
                if funct7 == 0x0:
                    self.ADD(self.regs[rs1], self.regs[rs2], rd)
                if funct7 == 0x20:
                    self.SUB(self.regs[rs1], self.regs[rs2], rd)

            if funct3 == 0x4 and funct7 == 0x0:
                self.XOR(self.regs[rs1], self.regs[rs2], rd)
            if funct3 == 0x6 and funct7 == 0x0:
                self.OR(self.regs[rs1], self.regs[rs2], rd)
            if funct3 == 0x7 and funct7 == 0x0:
                self.AND(self.regs[rs1], self.regs[rs2], rd)
            if funct3 == 0x1 and funct7 == 0x0:
                self.SHIFT(self.regs[rs1], self.regs[rs2], rd, 'l')
            if funct3 == 0x5 and funct7 == 0x0:
                self.SHIFT(self.regs[rs1], self.regs[rs2], rd)
            if funct3 == 0x5 and funct7 == 0x20:
                self.SHIFT(self.regs[rs1], self.regs[rs2], rd, 'r', True)

            if funct3 == 0x2 and funct7 == 0x0:  # slt
                self.COMPARE(rs1, rs2, rd, signed=True, cond='l')
            if funct3 == 0x3 and funct7 == 0x0:  # sltu
                self.COMPARE(rs1, rs2, rd, signed=False, cond='l')

            if funct3 == 0x0 and funct7 == 0x01:
                self.MUL(self.regs[rs1], self.regs[rs2], rd)
            if funct3 == 0x1 and funct7 == 0x01:
                self.MUL(self.regs[rs1], self.regs[rs2], rd)
            if funct3 == 0x2 and funct7 == 0x01:
                self.MUL(self.regs[rs1], self.regs[rs2], 'SU')
            if funct3 == 0x3 and funct7 == 0x01:
                self.MUL(self.regs[rs1], self.regs[rs2], 'U')
            if funct3 == 0x4 and funct7 == 0x01:
                self.DIV(self.regs[rs1], self.regs[rs2], rd)
            if funct3 == 0x5 and funct7 == 0x01:
                self.DIV(self.regs[rs1], self.regs[rs2], rd, False)
            if funct3 == 0x6 and funct7 == 0x01:
                self.REM(self.regs[rs1], self.regs[rs2], rd)
            if funct3 == 0x7 and funct7 == 0x01:
                self.REM(self.regs[rs1], self.regs[rs2], rd, False)
        # ------------ R type execution section ------------#

        # ------------ I type execution section ------------#

        if type_t == 'I1':
            rd = data_holder[12:7]
            funct3 = data_holder[15:12]
            rs1 = data_holder[20:15]
            imm = data_holder[32:20]
            print(
                "Type I1: imm: " + str(imm) + "\t func3: " + str(funct3) + "\t rs1: " + str(rs1) + "\t rd: " + str(rd))
            if funct3 == 0x0:
                self.ADD(self.regs[rs1], imm, rd)
            if funct3 == 0x4:
                self.XOR(self.regs[rs1], imm, rd)
            if funct3 == 0x6:
                self.OR(self.regs[rs1], imm, rd)
            if funct3 == 0x7:
                self.AND(self.regs[rs1], imm, rd)
            if funct3 == 0x1 and imm == 0x0:
                self.SHIFT(self.regs[rs1], imm, rd)
            if funct3 == 0x5 and imm == 0x0:
                self.SHIFT(self.regs[rs1], imm, rd)
            if funct3 == 0x5 and imm == 0x20:
                self.SHIFT(self.regs[rs1], imm, rd)
            if funct3 == 0x2:
                self.COMPARE(self.regs[rs1], imm, rd, 'le', signed= True)
            if funct3 == 0x3:
                self.COMPARE(self.regs[rs1], imm, rd, 'le', signed=False)

        if type_t == 'I2':
            rd = data_holder[12:7]
            funct3 = data_holder[15:12]
            rs1 = data_holder[20:15]
            imm = data_holder[32:20]
            print(
                "Type I2: imm: " + str(imm) + "\t func3: " + str(funct3) + "\t rs1: " + str(rs1) + "\t rd: " + str(rd))

            if funct3 == 0x0:
                self.LOAD(rd, rs1, imm)
            if funct3 == 0x1:
                self.LOAD(rd, rs1, imm, 2)
            if funct3 == 0x2:
                self.LOAD(rd, rs1, imm, 4)
            if funct3 == 0x4:
                self.LOAD(rd, rs1, imm, False)
            if funct3 == 0x5:
                self.LOAD(rd, rs1, imm, 2, False)

        if type_t == 'I3':
            print(
                "Type I3: imm: " + str(imm) + "\t func3: " + str(funct3) + "\t rs1: " + str(rs1) + "\t rd: " + str(rd))
            rd = data_holder[12:7]
            funct3 = data_holder[15:12]
            rs1 = data_holder[20:15]
            imm = data_holder[32:20]
            self.JALR(rd, rs1, imm)

        if type_t == 'I4':
            rd = data_holder[12:7]
            funct3 = data_holder[15:12]
            rs1 = data_holder[20:15]
            imm = data_holder[32:20]
            print(
                "Type I4: imm: " + str(imm) + "\t func3: " + str(funct3) + "\t rs1: " + str(rs1) + "\t rd: " + str(rd))

            if imm == 0x0:
                self.ecall()
            if imm == 0x1:
                self.ebreak()
            # ------------ I type execution section ------------#

            # ------------ S type execution section ------------#
        if type_t == 'S':
            rs1 = data_holder[20:15]
            rs2 = data_holder[25:20]
            funct3 = data_holder[15:12]
            # buffer = []
            # buffer.append(data_holder[7])
            # buffer.append(data_holder[8])
            # buffer.append(data_holder[9])
            # buffer.append(data_holder[10])
            # buffer.append(data_holder[11])
            # buffer.append(data_holder[25])
            # buffer.append(data_holder[26])
            # buffer.append(data_holder[27])
            # buffer.append(data_holder[28])
            # buffer.append(data_holder[29])
            # buffer.append(data_holder[30])
            # buffer.append(data_holder[31])



            imm = intbv(0)[12:]
            bits_order = [7, 8, 9, 10, 11, 25, 26, 27, 28, 29, 30, 31]
            counter = 0
            for i in range(12):
                imm += intbv(data_holder[bits_order[i]] << i)
                counter += 1
            print(
                "Type S: imm: " + str(imm) + "\t func3: " + str(funct3) + "\t rs1: " + str(rs1) + "\t rs2: " + str(rs2))


            # change the imm to intbv
            if funct3 == 0x0:
                self.STORE(rs1, rs2, imm, width=1)
            if funct3 == 0x1:
                self.STORE(rs1, rs2, imm, width=2)
            if funct3 == 0x2:
                self.STORE(rs1, rs2, imm, width=4)

            # ------------ S type execution section ------------#

            # ------------ B type execution section ------------#
        if type_t == 'B':
            buffer = []

            imm = intbv(0)[13:]
            bits_order = [8, 9, 10, 11, 25, 26, 27, 28, 29, 30, 7, 31]
            counter = 0
            for i in range(12):
                imm += intbv(data_holder[bits_order[i]] << i)
                counter += 1
            imm = int(intbv(imm)[12:].signed() << 1)
            print(int(imm))
            imm = intbv(imm).signed()[32:]
            # must make the intbv arg as an int
            funct3 = data_holder[15:12]
            rs1 = data_holder[20:15]
            rs2 = data_holder[25:20]

            print(
                "Type B: imm: " + str(imm) + "\t func3: " + str(funct3) + "\t rs1: " + str(rs1) + "\t rs2: " + str(rs2))

            if funct3 == 0x0:
                self.BRANCH(rs1, rs2, imm, 'e')
            if funct3 == 0x1:
                self.BRANCH(rs1, rs2, imm, 'ne')
            if funct3 == 0x4:
                self.BRANCH(rs1, rs2, imm, 'lt')
            if funct3 == 0x5:
                self.BRANCH(rs1, rs2, imm, 'ge')
            if funct3 == 0x6:
                self.BRANCH(rs1, rs2, imm, 'lt', False)
            if funct3 == 0x7:
                self.BRANCH(rs1, rs2, imm, 'ge', False)
            # ------------ B type execution section ------------#

            # ------------ U type execution section ------------#
        if type_t == 'U1':
            rd = data_holder[12:7]
            imm = data_holder[32:12]
            print("Type LUI: imm: " + str(imm) + "\t rd: " + str(rd))
            self.LUI(rd, imm)
        if type_t == 'U2':
            rd = data_holder[12:7]
            imm = data_holder[32:12]
            print("Type AUIPC: imm: " + str(imm) + "\t rd: " + str(rd))
            self.AUIPC(rd, imm)
            # ------------ U type execution section ------------#

        if type_t == 'J':
            rd = data_holder[21:]
            # buffer = []
            # buffer.append(0b0)
            # buffer.append(data_holder[21])
            # buffer.append(data_holder[22])
            # buffer.append(data_holder[23])
            # buffer.append(data_holder[24])
            # buffer.append(data_holder[25])
            # buffer.append(data_holder[26])
            # buffer.append(data_holder[27])
            # buffer.append(data_holder[28])
            # buffer.append(data_holder[29])
            # buffer.append(data_holder[30])
            # buffer.append(data_holder[20])
            # buffer.append(data_holder[12])
            # buffer.append(data_holder[13])
            # buffer.append(data_holder[14])
            # buffer.append(data_holder[15])
            # buffer.append(data_holder[16])
            # buffer.append(data_holder[17])
            # buffer.append(data_holder[18])
            # buffer.append(data_holder[19])
            # buffer.append(data_holder[31])

            imm = intbv(0)[21:]
            bits_order = [21,22,23,24,25,26,27,28,29,30,20,12,13,14,15,16,17,18,19,31]
            counter = 0
            for i in range(20):
                imm += intbv(data_holder[bits_order[i]] << i)
                counter += 1
            imm = intbv(imm << 1)[21:]

            print("Type JAL: imm: " + str(imm) + "\t rd: " + str(rd))

            self.JAL(rd, imm)


# if __name__ == '__main__':
#     # Testing area:
#     x = CPU()
#
#     reg = [intbv(0)[32:0] for i in range(32)]
#     print("==================")
#     print(reg[intbv(4)])
#     # x.exc_arithmetic(0,0)
#     y = 5
#     ar = bytearray(5)
#     ar[1] = 255
#     print(ar[1])
#     print(ar)
#     print(x)  # Notes:
#     # We can use bytearray indices as numbers. for example if x is a bytearray, we can access like
#     # x[3] -> will return the fourth byte in the array. Just like normal arrays. it will be returned as integer.
#     # We can also manipulate it like integer or bits. It is acutally binary. we can do x[3] & 0b0001 or
#     # x[3] = y + 4 or any other operation, and it will be stored back as a byte.
#     # ----- intbv notes ----- #
#     # if you want to store 0b1100 as signed number (should be -4 not 12) then you must do the following:
#     # 1-    x = intbv(0b1100, min=0, max=16) -> note that we defined min and max. this is a must. alternativly,
#     #       ... we can also define number of bits instead of min and max. this will also work
#     # 2-    y = x.signed() -> returns -4
#     # If we didn't define min and max in x, then y will return 12.
#     # ----------------------------- test -----------------------------#
#
#     x = list()
#     x.append(0b00001111110000010000010100010111.to_bytes(4, byteorder='little'))  # store instruction as little endian
#     print(x[0])  # x[0] contains a 4 bytes stored as (byte) data type.
#     xint = int.from_bytes(x[0], 'little')  # convert x[0] from type byte into integer type.
#     ibv1 = intbv(xint)[32:0]  # convert xint into intbv
#     print(ibv1[5:])  # we can slice it like this
#
#     print("========================")
#     ibv = intbv('111111000001000001010001')[24:0]
#     print(ibv.signed() + 1)
