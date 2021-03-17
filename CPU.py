



# registers
x0=[0]*32
x1=[0]*32
x2=[0]*32
x3=[0]*32
x4=[0]*32
x5=[0]*32
x6=[0]*32
x7=[0]*32
x8=[0]*32
x9=[0]*32
x10=[0]*32
x11=[0]*32
x12=[0]*32
x13=[0]*32
x14=[0]*32
x15=[0]*32
x16=[0]*32
x17=[0]*32
x18=[0]*32
x19=[0]*32
x20=[0]*32
x21=[0]*32
x22=[0]*32
x23=[0]*32
x24=[0]*32
x25=[0]*32
x26=[0]*32
x27=[0]*32
x28=[0]*32
x29=[0]*32
x30=[0]*32
x31=[0]*32



# make memory so you can fetch from it


test_memory = bytearray(b'\x13\xff\x01\x08')
print(test_memory)

#make a method to fetch from memory

def fetch_data():
    #The fetched data hold variable =  memory list variable[program_counter]
    data_holder=1
    return data_holder

#-------------------------- decode section ------------------------------------#

# check op code first 
