import sys
from subprocess import Popen, PIPE
import re

BLANK_SPEC = """module CALCBOUND
    imports MEV
    rule <k>
            %s
         => ?X
     </k>
    <S> ( (Uniswap in 0) |-> 0 (Uniswap in SAI) |-> 0 ) =>?Y0:Map </S>
    <M> .Set => ?Y1:Set </M>
    <B> .List => ?Y2:List </B>
    <P> .Map => ?Y3:Map </P>
    <V> .Map => ?Y4:Map </V>
    ensures ( ({?Y0[0 in SAI]}:>Int <=Int 0) andBool ?X ==K DONE) orBool (?X ==K FAIL)
endmodule
"""

def find_mev_cdp(program, outfile):
    global BLANK_SPEC
    output = ""
    spec = BLANK_SPEC % (program)
    open("output/calcbound.k", "w").write(spec)
    print("Starting proof...")
    sys.stdout.flush()
    pipe = Popen("kprove -v --debug --default-claim-type all-path --z3-impl-timeout 500 output/calcbound.k", shell=True, stdout=PIPE, stderr=PIPE)
    output = pipe.stdout.read() + pipe.stderr.read()
    output = str(output, "utf-8")
    print(output)
    if "#True" not in output:
        print("MEV FOUND!")
        print("Writing MEV configuration to", outfile, "...")
        open(outfile, "w").write(output)
        return

def main():
    PROGRAM = open(sys.argv[1]).read()
    find_mev_cdp(PROGRAM, "output/calcmev.out")

if __name__ == '__main__':
    main()
