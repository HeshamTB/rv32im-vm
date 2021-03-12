import unittest
from mem import Memory

class MemoryTestSuit(unittest.TestCase):
    ram = None
    def setUp(self):
        self.ram = Memory(100)

    def test_init_mem(self):
        size = self.ram.getSize()
        self.assertEqual(size, 100)
    
    def test_mem_write(self):
        self.ram.write(2, int(22).to_bytes(1, 'little')) # Write value 22 to address 2
        self.assertEqual(self.ram.readAsInt(2), 22)
        
    def test_mem_readAsInt(self):
        val = self.ram.readAsInt(2)
        self.assertEqual(val, 0)
    
    def test_mem_comprehinsive_numbers(self):
        pass


if __name__ == '__main__':
    unittest.main()