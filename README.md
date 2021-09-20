# Buddha Machine Firmware Tool

A tool for decoding and re-encoding Buddha Machine flash images. Based on work by Malvineous and Hjalfi at
https://old.reddit.com/r/BigCliveDotCom/comments/pmt390/buddha_machine_teardown_with_flash_dump/ as well as
work by AlexGuo1998 and Prehistoricman at https://youtu.be/LNpbvyLIvN0 .

Right now it only extracts the binary code loaded into the 8051 microcontroller.  The audio files themselves
use an unknown encoding that has not been figured out yet.

The extracted firmware can be found in the firmware/ directory.  The disassembled files were generated with
`mame`'s unidasm tool:
    unidasm fileparts.00.code.app.part-14.bin -arch axc51core >fileparts.00.code.app.part-14.bin.asm

To extract everything, simply run:

    python3 bmfwtool.py buddha.bin -p fileparts -c fullfile.bin

```
python3 bmfwtool.py buddha.bin -p fileparts -c fullfile.bin

Header Checksum: pass
Table Checksum: pass
File # 0 "code.app" Checksum: pass
  Added App entry # 14
  Added App entry # 0, Table Checksum: pass, Data Checksum: pass
  Added App entry # 1, Table Checksum: pass, Data Checksum: pass
  Added App entry # 2, Table Checksum: pass, Data Checksum: pass
  Added App entry # 3, Table Checksum: pass, Data Checksum: pass
  Added App entry # 4, Table Checksum: pass, Data Checksum: pass
  Added App entry # 5, Table Checksum: pass, Data Checksum: pass
  Added App entry # 6, Table Checksum: pass, Data Checksum: pass
  Added App entry # 7, Table Checksum: pass, Data Checksum: pass
  Added App entry # 8, Table Checksum: pass, Data Checksum: pass
  Added App entry # 9, Table Checksum: pass, Data Checksum: pass
  Added App entry # 10, Table Checksum: pass, Data Checksum: pass
  Added App entry # 11, Table Checksum: pass, Data Checksum: pass
  Added App entry # 12, Table Checksum: pass, Data Checksum: pass
  Added App entry # 13, Table Checksum: pass, Data Checksum: pass
File # 1 "play_list.bin" Checksum: pass
File # 2 "id_list.bin" Checksum: pass
File # 3 "n01.f1a" Checksum: pass
File # 4 "n02.f1a" Checksum: pass
File # 5 "n03.f1a" Checksum: pass
File # 6 "n04.f1a" Checksum: pass
File # 7 "n05.f1a" Checksum: pass
File # 8 "n06.f1a" Checksum: pass
File # 9 "n07.f1a" Checksum: pass
File # 10 "n08.f1a" Checksum: pass
File # 11 "n09.f1a" Checksum: pass
File # 12 "n10.f1a" Checksum: pass
File # 13 "n11.f1a" Checksum: pass
File # 14 "n12.f1a" Checksum: pass
File # 15 "n13.f1a" Checksum: pass
File # 16 "n14.f1a" Checksum: pass
File # 17 "n15.f1a" Checksum: pass
File # 18 "n16.f1a" Checksum: pass
File # 19 "n17.f1a" Checksum: pass
File # 20 "n18.f1a" Checksum: pass
File # 21 "n19.f1a" Checksum: pass
File # 22 "n20.f1a" Checksum: pass
File # 23 "n21.f1a" Checksum: pass
File # 24 "n22.f1a" Checksum: pass
File # 25 "n23.f1a" Checksum: pass
File # 26 "n24.f1a" Checksum: pass
File # 27 "n25.f1a" Checksum: pass
File # 28 "n26.f1a" Checksum: pass
File # 29 "n27.f1a" Checksum: pass
File # 30 "n28.f1a" Checksum: pass
File # 31 "n29.f1a" Checksum: pass
File # 32 "n30.f1a" Checksum: pass
File # 33 "n31.f1a" Checksum: pass
File # 34 "n32.f1a" Checksum: pass
File # 35 "n33.f1a" Checksum: pass
File # 36 "n34.f1a" Checksum: pass
File # 37 "n35.f1a" Checksum: pass
File # 38 "n36.f1a" Checksum: pass
File # 39 "n37.f1a" Checksum: pass
File # 40 "n38.f1a" Checksum: pass
File # 41 "n39.f1a" Checksum: pass
File # 42 "map_table.sys" Checksum: pass
Writing: fullfile.bin
Writing: fileparts.filetable.bin
Writing: fileparts.00.code.app.bin
Writing: fileparts.00.code.app.part-14.bin
Writing: fileparts.00.code.app.part-14-00.bin
Writing: fileparts.00.code.app.part-14-01.bin
Writing: fileparts.00.code.app.part-14-02.bin
Writing: fileparts.00.code.app.part-14-03.bin
Writing: fileparts.00.code.app.part-14-04.bin
Writing: fileparts.00.code.app.part-14-05.bin
Skipping 0-length section: fileparts.00.code.app.part-14-06.bin
Skipping 0-length section: fileparts.00.code.app.part-14-07.bin
Writing: fileparts.00.code.app.part-14-08.bin
Skipping 0-length section: fileparts.00.code.app.part-14-09.bin
Writing: fileparts.00.code.app.part-14-10.bin
Skipping 0-length section: fileparts.00.code.app.part-14-11.bin
Writing: fileparts.00.code.app.part-14-12.bin
Writing: fileparts.00.code.app.part-14-13.bin
Writing: fileparts.01.play_list.bin.bin
Writing: fileparts.02.id_list.bin.bin
Writing: fileparts.03.n01.f1a.bin
Writing: fileparts.04.n02.f1a.bin
Writing: fileparts.05.n03.f1a.bin
Writing: fileparts.06.n04.f1a.bin
Writing: fileparts.07.n05.f1a.bin
Writing: fileparts.08.n06.f1a.bin
Writing: fileparts.09.n07.f1a.bin
Writing: fileparts.10.n08.f1a.bin
Writing: fileparts.11.n09.f1a.bin
Writing: fileparts.12.n10.f1a.bin
Writing: fileparts.13.n11.f1a.bin
Writing: fileparts.14.n12.f1a.bin
Writing: fileparts.15.n13.f1a.bin
Writing: fileparts.16.n14.f1a.bin
Writing: fileparts.17.n15.f1a.bin
Writing: fileparts.18.n16.f1a.bin
Writing: fileparts.19.n17.f1a.bin
Writing: fileparts.20.n18.f1a.bin
Writing: fileparts.21.n19.f1a.bin
Writing: fileparts.22.n20.f1a.bin
Writing: fileparts.23.n21.f1a.bin
Writing: fileparts.24.n22.f1a.bin
Writing: fileparts.25.n23.f1a.bin
Writing: fileparts.26.n24.f1a.bin
Writing: fileparts.27.n25.f1a.bin
Writing: fileparts.28.n26.f1a.bin
Writing: fileparts.29.n27.f1a.bin
Writing: fileparts.30.n28.f1a.bin
Writing: fileparts.31.n29.f1a.bin
Writing: fileparts.32.n30.f1a.bin
Writing: fileparts.33.n31.f1a.bin
Writing: fileparts.34.n32.f1a.bin
Writing: fileparts.35.n33.f1a.bin
Writing: fileparts.36.n34.f1a.bin
Writing: fileparts.37.n35.f1a.bin
Writing: fileparts.38.n36.f1a.bin
Writing: fileparts.39.n37.f1a.bin
Writing: fileparts.40.n38.f1a.bin
Writing: fileparts.41.n39.f1a.bin
Writing: fileparts.42.map_table.sys.bin
```

    python3 bmfwtool.py -h

```
usage: bmfwtool.py [-h] [-f] [-c CLEAR] [-e ENCODED] [-p PREFIX] INFILE

Buddha Machine firmware tool

positional arguments:
  INFILE                Input file

optional arguments:
  -h, --help            show this help message and exit
  -f, --force           Force (allow) overwriting of the output file(s)
  -c CLEAR, --clear CLEAR
                        Outputs the dump as a single file in the clear
  -e ENCODED, --encode ENCODED
                        Outputs the dump as a single encoded file
  -p PREFIX, --prefix PREFIX
                        Outputs the multiple parts as different files named
                        with this prefix

https://old.reddit.com/r/BigCliveDotCom/comments/pmt390/buddha_machine_teardow
n_with_flash_dump/ Youtube video of BigClive's teardown:
https://youtube.com/watch?v=LNpbvyLIvN0
```