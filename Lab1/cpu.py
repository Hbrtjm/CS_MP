
class Cpu:
  def __init__(self, mem, undefined_cb=None):
    self.mem = mem
    self.undefined_cb = undefined_cb
    self.reset()
    self.__opcode_h = 0
    self.__opcode_l = 0
  
  def reset(self):
    self.state = 0
    self.mem_address = 0
    self.mem_data_r = 0
    self.mem_data_w = 0
    self.pc = 0
    self.r0 = 0
    self.r1 = 0
    self.opcode = 0
    
  
  def next_cycle(self):
    if self.state == 0:
      self.state = 1
      self.mem_address = self.pc
      self.mem_data_r = self.mem[self.mem_address]
    elif self.state == 1:
      self.state = 2
      self.opcode = self.mem_data_r
      self.pc = self.pc + 1
      
    elif self.state == 2:
      self.state = 3
      self.__opcode_h = (self.opcode & 0xF0) >> 4
      self.__opcode_l = self.opcode & 0x0F
      # jmp and data processing (opcode bit 7 is 0)
      if self.__opcode_h == 0x0:
        self.pc = self.__opcode_l
      elif self.__opcode_h == 0x2:
        self.r0 = self.r0 + self.r1
      # Now adding new instructions
      elif self.__opcode_h == 0x3:  # Adding R0 to R1
        self.r1 = self.r1 + self.r0
      elif self.__opcode_h == 0x4:  # Multiply R1 * R0, store result in R1 (high) and R0 (low)
        self.r1 = (self.r0 * self.r1 >> 4) & 0x0F  # More significant byte to R1
        self.r0 = self.r0 * self.r1 & 0x0F  # Less significant byte to R0
      elif self.__opcode_h == 0x8:
        self.r0 = self.__opcode_l
      elif self.__opcode_h == 0x9:
        self.r1 = self.__opcode_l
      elif self.__opcode_h == 0xA:
        self.r0 = self.r1
      elif self.__opcode_h == 0xB:
        self.r1 = self.r0
      # load and store (opcode bit 7 is 1)
      elif self.__opcode_h == 0xC:
        self.mem_address = self.__opcode_l
      elif self.__opcode_h == 0xD:
        self.mem_address = self.__opcode_l
      elif self.__opcode_h == 0xE:
        self.mem_address = self.__opcode_l
        self.mem_data_w = self.r0
      elif self.__opcode_h == 0xF:
        self.mem_address = self.__opcode_l
        self.mem_data_w = self.r1
      else:
        self.undefined_cb(self.mem_address, self.__opcode_h)
        
    elif self.state == 3:
      self.state = 0
      if self.__opcode_h == 0xC:
        self.r0 = self.mem[self.mem_address]
      elif self.__opcode_h == 0xD:
        self.r1 = self.mem[self.mem_address]
      elif self.__opcode_h == 0xE:
        self.mem[self.mem_address] = self.mem_data_w
      elif self.__opcode_h == 0xF:
        self.mem[self.mem_address] = self.mem_data_w
      # else:
      #   self.undefined_cb(self.mem_address, self.__opcode_h)
        
    else:
      print(f'something went wrong, state should not be >3')
    self.debug_dump()
    

  def __intlist_to_hex_str(self,intlist):
    return f"{' '.join(f'{n:02X}' for n in intlist)}"

  def debug_dump(self):
    print(f"c={self.state:X} r0={self.r0:X} r1={self.r1:X} \
pc={self.pc:X} A={self.mem_address:X} R={self.mem_data_r:02X} \
W={self.mem_data_w:02X} M: {self.__intlist_to_hex_str(self.mem)}")
