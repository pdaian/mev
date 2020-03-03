import os

out = open('out2').read()
states = out.count("#Or")
print("Found %d states." % (states))

max_amt = -1

for line in out.splitlines():
    if "0 in 0 |-" in line and  line.index("0 in 0 |-") == 8:
        amt = int(line.split()[-1])
        max_amt = amt if amt > max_amt else max_amt
        print(amt)

print("miner makes at most %d" % (max_amt))
os.system("grep -C 20 '0 in 0 |-> %d' out" % (max_amt))
