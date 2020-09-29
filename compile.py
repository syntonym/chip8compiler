from jinja2 import Template
from typing import Dict


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

def hexa(i):
    h = hex(i)
    if len(h) == 3:
        return "0" + h[2]
    else:
        return h[2:]

for i in range(0, len(codes),2):
    print(hexa(codes[i]) + hexa(codes[i+1]))


with open("template.html") as f:
    template = Template(f.read())

rendered = template.render(ROM=",".join(str(op) for op in codes))

with open("out.html", mode="w") as f:
    f.write(rendered)
