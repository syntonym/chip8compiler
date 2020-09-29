from jinja2 import Template
from typing import Dict
import re

MNEMS = [
("0(...)", lambda x: "Deprecated (Machine Exec)"),
("00E0"  , lambda : "Clear"),
("00EE"  , lambda : "Return"),
("1(...)"  , lambda x: f"Jump {x}"),
("2(...)"  , lambda x: f"Exec {x}"),
("3(.)(..)"  , lambda x, y: f"Skip v{x}=={y}"),
("4(.)(..)"  , lambda x, y: f"Skip v{x}!={y}"),
("5(.)(.)0"  , lambda x, y: f"Skip v{x}==v{y}"),
("6(.)(..)"  , lambda x, y: f"v{x} = {y}"),
("7(.)(..)"  , lambda x, y: f"v{x} += {y}"),
("8(.)(.)0"  , lambda x, y: f"v{x} = v{y}"),
("8(.)(.)1"  , lambda x, y : f"v{x} |= v{y}"),
("8(.)(.)2"  , lambda x, y: f"v{x} &= v{y}"),
("8(.)(.)3"  , lambda x, y: f"v{x} ^= v{y}"),
("8(.)(.)4"  , lambda x, y: f"v{x} += v{y}"),
("8(.)(.)5"  , lambda x, y: f"v{x} -= v{y}"),
("8(.)(.)6"  , lambda x, y: f"v{x} =>> v{y}"),
("8(.)(.)7"  , lambda x, y: f"v{x} = v{y} - vX"),
("8(.)(.)E"  , lambda x, y: f"v{x} =<< v{y}"),
("9(.)(.)0"  , lambda x, y: f"Skip{x}!={y}"),
("A(...)"  , lambda x: f"i = {x}"),
("B(...)"  , lambda x: f"Jump {x} + v0"),
("C(.)(..)"  , lambda x, y: f"v{x} = Rand && {y}"),
("D(.)(.)(.)"  , lambda x, y, z: f"Sprite {x} {y} h{z}"),
("E(.)9E"  , lambda x: f"SkipKey v{x}"),
("E(.)A1"  , lambda x: f"SkipNotKey v{x}"),
("F(.)07"  , lambda x: f"DelayTo v{x}"),
("F(.)0A"  , lambda x: f"Key v{x}"),
("F(.)15"  , lambda x: f"v{x} ToDelay"),
("F(.)18"  , lambda x: f"Sound v{x}"),
("F(.)1E"  , lambda x: f"I+=v{x}"),
("F(.)29"  , lambda x: f"i = Font v{x}"),
("F(.)33"  , lambda x: f"StoreBinary v{x}"),
("F(.)55"  , lambda x: f"StoreRegisters v{x}"),
("F(.)65"  , lambda x: f"LoadRegisters v{x}"),
]


with open("code") as f:
    lines = f.readlines()

out = []


counter = 512
labels : Dict[str, int] = {}

def op(s):
    out.append(int(s, 16))
    global counter
    counter += 1

def fake(s):
    out.append(s)
    global counter
    counter += 2

def location(s):
    if s[0] == "@":
        l = labels[s[1:]]
    else:
        l = int(s, 16)
    return l // 0xff, l % 0xff

for line in lines:
    l = line.split(" ")
    l[-1] = l[-1].strip()
    if l[0] == "set":
        fake("A" + l[1])
    elif l[0] == "jump":
        fake("1"+ l[1])
    elif l[0] == "label":
        labels[l[1]] = counter
    elif l[0][0] == "v":
        op("6" + l[0][1])
        op(l[1])
    elif l[0] == "sprite":
        op("D" + l[1][1])
        op(l[2][1] + l[3])
    elif l[0] == "inc":
        op("F" + l[1][1]) # l1 = "vX"
        op("18")
    elif l[0] == "key":
        v = l[1][1]
        op("F" + v)
        op("0A")
    elif l[0] == "add":
        op("7" + l[1][1])
        op(l[2])
    else:
        op(l[0])

codes = []

for c in out:
    if type(c) == str:
        l1, l2 = location(c[1:])
        codes.append(int(c[0] + hex(l1)[2:], 16))
        codes.append(l2)
    else:
        codes.append(c)

for label in labels:
    print(f"{label}: {labels[label]}")


def hexa(i):
    h = hex(i)
    if len(h) == 3:
        return "0" + h[2]
    else:
        return h[2:]


def get_mem(code):
    for mem in MNEMS:
        m = re.match(mem[0], code)
        if m:
            return mem[1](*m.groups())
    return "?"


for i in range(0, len(codes), 2):
    h1, h2 = hexa(codes[i]).upper(), hexa(codes[i+1]).upper()
    mem = get_mem(h1+h2)
    print(f"{i+512}  {h1} {h2}    {mem}")


with open("template.html") as f:
    template = Template(f.read())

rendered = template.render(ROM=",".join(str(op) for op in codes))

with open("out.html", mode="w") as f:
    f.write(rendered)
