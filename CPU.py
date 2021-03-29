from myhdl import intbv, bin
from mem import Memory


class CPU:
    """
        In this class, we have the following components/sections:
            1- Registers (just a typical array, contains 32 slots. Each slot stores integers or intbv, not decided yet)
            2- Fetch instructions
            3- Decode instructions
            4- Execute instructions
    """

    # ALU Inner class
    # TODO: Consider removing this sub-class since it serves no purpose anymore
    class ALU:
        """
            A sub class that has a function for each major arithmetic and logic operation (e.g. ADD, SUB, SHIFT, etc).
            These major functions should be called from within the cpu, by the executioner function.


        """


        # TODO: Think about the two functions commented below. If they serve no purpose anymore, delete them.


    # Constructor of CPU
    def __init__(self):
        """
            CPU constructor
            This initializes the registers
            Input: NONE
        """
        self.regs = [intbv(0)[32:0] for i in range(32)]  # The Registers. Just a typical list
        self.alu_unit = self.ALU()  # Consider removing it later
        self.pc = 0
        self.test_mem = Memory(100)  # just for testing.

    # =========== Fetching Area =========== #
    """
        Fetch the next instruction from the memory.
    """

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
    def ADD(self, arg1: intbv, arg2: intbv) -> int:
        return arg1 + arg2

    def SUB(self, arg1: intbv, arg2: intbv) -> int:
        return self.ADD(arg1, -arg2)

    def OR(self, arg1, arg2):
        return arg1 | arg2

    def XOR(self, arg1, arg2):
        return arg1 ^ arg2

    def AND(self, arg1, arg2):
        return arg1 & arg2

    def SHIFT(self, arg1: intbv, arg2: intbv, dir='r', signed=False):  # needs testing
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
                return arg1.signed() >> arg2.signed()
            else:
                return arg1 >> arg2  # arg1 is not signed number
        elif dir == "l":
            return arg1 << arg2

    def COMPARE(self, arg1: intbv, arg2: intbv, cond="e", signed=True):
        """
        Comapre arg1 and arg2.
        Args:
            arg1: first argument
            arg2: second argument
            cond: comparison condition. e for equal, l for less, and g for greater.
            signed: Boolean flag for sign. By default is True. Set to False in case inputs are unsigned
        Returns: Boolean. indicates whether comparison result is true or false
        """
        if signed:  # Check the sign
            arg1 = arg1.signed()
            arg2 = arg2.signed()
        # Check the conditions
        if cond == "e":
            return arg1 == arg2
        elif cond == "l":
            return arg1 < arg2
        elif cond == "g":
            return arg1 > arg2

    def MUL(self, arg1: intbv, arg2: intbv, sign='S'):
        # I considered the notation (s)(u) to mean arg1 is signed, arg2 not signed
        if sign.capitalize() == 'SU':
            return arg1.signed() * arg2.unsigned()
        elif sign.capitalize() == 'U':
            return arg1 * arg2
        elif sign.capitalize() == 'S':
            return arg1.signed() * arg2.signed()
        else:
            print("Error: condition " + sign + " is not defined for MUL function")

    def DIV(self, arg1: intbv, arg2: intbv, signed=True):
        if signed:
            return arg1.signed() // arg2.signed()
        return arg1 // arg2

    def REM(self, arg1: intbv, arg2: intbv, signed=True):
        if signed:
            arg1.signed() % arg2.signed()
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
        target_address = self.ADD(imm, src)
        loaded_bytes = None
        if width == 1:
            loaded_bytes = self.test_mem.read(target_address)
        elif width == 2:
            loaded_bytes = self.test_mem.readHalfWord(target_address)
        elif width == 4:
            loaded_bytes = self.test_mem.readWord(target_address)
        else:
            print("Error: please enter valid load width")
            exit(0)
        # Store the loaded byte as an integer in the destination reg
        self.regs[rd] = int.from_bytes(loaded_bytes, 'little')

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
        src2 = self.regs[rs2].to_bytes(width, 'little')
        target_address = self.ADD(imm, src1)
        # Loop, each time store one byte from src2 in the memory.
        for i in range(width):
            store_byte = src2[i].to_bytes(1, 'little')
            self.test_mem.write(target_address+i, store_byte)

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
            res = self.COMPARE(val1, val2, cond='e', signed=signed)
        elif cond == 'ne':
            res = not self.COMPARE(val1, val2, cond='e', signed=signed)
        elif cond == 'lt':
            res = self.COMPARE(val1, val2, cond='l', signed=signed)
        elif cond == 'ge':
            res = self.COMPARE(val1, val2, cond='g', signed=signed) or self.COMPARE(val1, val2, cond='e', signed=signed)
        else:
            print("Error: Please enter valid comparison condition")

        if res:
            self.pc += imm

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
        imm = imm<<1
        imm = intbv(imm)[21:0]
        self.regs[rd] = self.pc + 4  # Save return address in rd
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
        self.regs[rd] = self.pc+4
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
        self.regs[rd] = imm

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
        self.regs[rd] = self.pc + imm

    # -------------------------- System calls -------------------------- #
    # TODO: Implement system calls.
    def ecall(self):
        pass

    def ebreak(self):
        pass

    # TODO: Following function was to be replaced by many functions, for each format (for example exc_R) ...
    #  ... but I decided to change that structure a bit and made functions for each major operation.
    #  this function now serves no purpose but its content can be used somewhere else. Consider deleting it later.
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

    def Fahd(self,memory_snippet):
        # ----------------------------- test -----------------------------#

        # Here we have data an example of data fetched from memory
        memory = []
        memory.append(0b00001111110000010000010100010111.to_bytes(4, byteorder='little'))
        # four_byte=memory[0]
        buffer_int = int.from_bytes(memory[0], 'little')
        data_holder = intbv(buffer_int)[32:0]
        rd = 0b0
        rs1 = 0b0
        rs2 = 0b0
        funct3 = 0b0
        funct7 = 0b0
        imm = 0b0
        imm1 = 0b0
        imm2 = 0b0
        # memory has 4 bytes and the opcode will take the first byte that contains the opcode.
        # opcode=four_byte[:1]
        # binary_string = "{:08b}".format(int(opcode.hex(),16)) # change the format to a string showing the byte bits.
        key_opcodes = [0b0110011, 0b0010011, 0b0000011, 0b1100111, 0b1110011, 0b0100011, 0b1100011, 0b0110111,
                       0b0010111,
                       0b1101111]  # opcode for R I S B U J types.

        type = ''

        for i in range(len(key_opcodes)):
            if data_holder[6:0] == key_opcodes[i]:
                print('match found')

                if i == 0:
                    print('Type is: ', 'R')
                    type = 'R'
                if i == 1:
                    print('Type is: ', 'I')
                    type = 'I1'
                if i == 2:
                    print('Type is: ', 'I')
                    type = 'I2'
                if i == 3:
                    print('Type is: ', 'I')
                    type = 'I3'
                if i == 4:
                    print('Type is: ', 'I')
                    type = 'I4'
                if i == 5:
                    print('Type is: ', 'S')
                    type = 'S'
                if i == 6:
                    print('Type is: ', 'B')
                    type = 'B'
                if i == 7:
                    print('Type is: ', 'U')
                    type = 'U'
                if i == 8:
                    print('Type is: ', 'U')
                    type = 'U'
                if i == 9:
                    print('Type is: ', 'J')
                    type = 'J'

        #------------ R type execution section ------------#
        if type == 'R':
            rd = data_holder[11:7]
            rs1 = data_holder[19:15]
            rs2 = data_holder[24:20]
            funct3 = data_holder[14:12]
            funct7 = data_holder[31:25]
            # look for the correct instruction via func3 and func7
            if funct3 == 0b000:
                if funct7 == 0x0:
                    self.ADD(rs1, rs2)
                if funct7 == 0x20:
                    self.SUB(rs1,rs2)

            if funct3 ==0x4 and funct7==0x0:
                self.XOR(rs1,rs2)
            if funct3==0x6 and funct7==0x0:
                self.OR(rs1,rs2)
            if funct3==0x7 and funct7==0x0:
                self.AND(rs1,rs2)
            if funct3==0x1 and funct7==0x0:
                self.SHIFT(rs1,rs2,'l')
            if funct3==0x5 and funct7==0x0:
                self.SHIFT(rs1,rs2)
            if funct3==0x5 and funct7==0x20:
                self.SHIFT(rs1,rs2,'r',True)

            if funct3 == 0x2 and funct7 == 0x0: # the execution method here is not yet added
                print()

            if funct3 == 0x3 and funct7 == 0x0:# the execution method here is not yet added
                print()
        # ------------ R type execution section ------------#

        #------------ I type execution section ------------#

        if type == 'I1':
            rd=data_holder[11:7]
            funct3=data_holder[14:12]
            rs1=data_holder[19:15]
            imm=data_holder[31:20]

            if funct3 == 0x0:
                self.ADD(rs1,imm)
            if funct3 == 0x4:
                self.XOR(rs1,imm)
            if funct3 == 0x6:
                self.OR(rs1,imm)
            if funct3 == 0x7:
                self.AND(rs1,imm)
            if funct3 == 0x1:
                self.SHIFT()
            print()

        if type == 'I2':
            rd = data_holder[11:7]
            funct3 = data_holder[14:12]
            rs1 = data_holder[19:15]
            imm = data_holder[31:20]


        if type =='I3':
            print()

        if type =='I4':
            print()
        # ------------ I type execution section ------------#



        # ------------ S type execution section ------------#
        if type == 'S':
            rs1=data_holder[19:15]
            rs2=data_holder[24:20]
            buffer=[]
            buffer.append(data_holder[7])
            buffer.append(data_holder[8])
            buffer.append(data_holder[9])
            buffer.append(data_holder[10])
            buffer.append(data_holder[11])
            buffer.append(data_holder[25])
            buffer.append(data_holder[26])
            buffer.append(data_holder[27])
            buffer.append(data_holder[28])
            buffer.append(data_holder[29])
            buffer.append(data_holder[30])
            buffer.append(data_holder[31])

            imm = intbv(buffer)[32:0]
            # change the imm to intbv
            if funct3 == 0x0:
                self.STORE(rs1,rs2,imm)
            if funct3 == 0x1:
                self.STORE(rs1,rs2,imm,2)
            if funct3 == 0x2:
                self.STORE(rs1,rs2,imm,4)

        # ------------ S type execution section ------------#

        # ------------ B type execution section ------------#
        if type=='B':
            buffer=[]

            buffer.append(data_holder[8])
            buffer.append(data_holder[9])
            buffer.append(data_holder[10])
            buffer.append(data_holder[11])
            buffer.append(data_holder[25]) # 10:5
            buffer.append(data_holder[26])
            buffer.append(data_holder[27])
            buffer.append(data_holder[28])
            buffer.append(data_holder[29])
            buffer.append(data_holder[30])
            buffer.append(data_holder[7])
            buffer.append(data_holder[31])
            #must make the intbv arg as an int

            imm = intbv(buffer)[32:0]
            funct3 = data_holder[14:12]
            rs1 = data_holder[19:15]
            rs2 = data_holder[24:20]

            if funct3 == 0x0:
                self.BRANCH(rs1,rs2,imm,'e')
            if funct3 == 0x1:
                self.BRANCH(rs1,rs2,imm,'ne')
            if funct3 == 0x4:
                self.BRANCH(rs1,rs2,imm,'lt')
            if funct3 == 0x5:
                self.BRANCH(rs1,rs2,imm,'ge')
            if funct3 == 0x6:
                self.BRANCH(rs1,rs2,imm,'lt',False)
            if funct3 == 0x7:
                self.BRANCH(rs1,rs2,imm,'ge',False)
        # ------------ B type execution section ------------#

        # ------------ U type execution section ------------#
        if type == 'U':
            rd = data_holder[11:7]
            imm = data_holder[31:12]
            self.LUI(rd, imm)
        # ------------ U type execution section ------------#

        if type == 'J':
            rd=data_holder[11:7]






        # ----------------------------- test -----------------------------#




memory = []
memory.append(0b00001111110000010000010100010111.to_bytes(4, byteorder='little'))
# four_byte=memory[0]
buffer_int = int.from_bytes(memory[0], 'little')
data_holder = intbv(buffer_int)[32:0]
print(data_holder[0]==0x1)
th=[1,2,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32]
print('start working!')
buffer= []
print(buffer)
buffer.append(th[0:4])
buffer.append(th[5:7])
print(buffer)