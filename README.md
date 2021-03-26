# RV32IM-VM

A simulated RISCV CPU and memory that excecutes compiled programs.

## System call layer
**WIP**
System calls invoked by ecall. The table below shows how to setup the the registers.
|SYSCALL| a0 | a1 |a2| a7
|--|--|--|--|--|
| EXIT | Return code |--| --- | 0x00
| PRINT | std[err\|out] |Content address| Read length | 0x40


