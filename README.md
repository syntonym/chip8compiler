This is a chip8 compiler. See octo, chip8 and octojam.

`compile.py` compiles the file `code` into CHIP8, which then gets injected into
`template.html`, which contains a CHIP8 VM. The result is written to
`out.html` which can be openend to see the file `code` running.

`compile.py` takes HEX encoded (in UTF-8) and outputs it into the code
the CHIP8 vm expects (integers in UTF-8). That means the text `63 00`
stores the number `00` into register `3` (for reference see http://mattmik.com/files/chip8/mastering/chip8.html )

Additionally `compile.py` has some inbuild commands or mmemotics.
Currently supported:

| code           | meaning                                                                                | CHIP8 code |
| ---            | ---                                                                                    | ---        |
| set XXX        | set register i to number XXX                                                           | AXXX       |
| jump XXX       | jump to code XXX                                                                       | 1XXX       |
| label WORD     | remember this location as WORD, see labeling below                                     | no opcode  |
| vY XX          | set register Y to XX                                                                   | 6YXX       |
| sprite vX vY Z | draw sprite (memory location i) at screen location register X register Y with height Z | FXYZ       |
| inc XX         | this has a bug, don't use it. I have no clue what it does.                             | ??         |
| key Y          | wait for key press and write to register Y                                             | FY0A       |
| add Y XX       | add value XX to register Y                                                             | 7YXX       |

labeling

To make it easier to jump to code locations and to draw sprites, labels
can give a (human understandable) name to a code location. `label XX`
remembers the current code location and the name can then be used by the
set and jump macros by writing `@LABEL` instead of a memory address.
Example:

```
set @sprite
label mainloop
sprite v1 v2 8
add 1 v1
jump @mainloop
label sprite
[sprite here]
```

This first sets register i to the sprite stored after label `sprite`,
then draws it to the screen with the coordinates v1 and v2 (sprite has
height 8), then adds 1 to the register v1 and jumps back to sprite
drawing.

Basically this repeatedly draws the sprite with a different x
coordinate.
