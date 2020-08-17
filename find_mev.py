import sys
from subprocess import Popen, PIPE
import re

BLANK_SPEC = """module BOUND
    imports MEV
    rule <k>
            0 in 0 gets 0;
            0 in SAI gets 0;
            0 bites vault %s;
            %s
         => ?X
     </k>
    <S> ( (Uniswap in 0) |-> 13 (Uniswap in SAI) |-> 56 ) =>?S:Map </S>
    <M> .Set => ?_:Set </M>
    <B> .List => ?_ </B>
    <P> .Map => ?_ </P>
    <V> .Map => ?_ </V>
    ensures ( ({?S[0 in SAI]}:>Int <=Int 0) andBool ?X ==K DONE) orBool (?X ==K FAIL)
endmodule
"""

def find_mev_cdp(program, outfile, starting_value, end_value):
    global BLANK_SPEC
    for v in range(starting_value, end_value+1):
        output = ""
        spec = BLANK_SPEC % (v, program)
        open("bound.k", "w").write(spec)
        print("Starting proof..." + str(v))
        sys.stdout.flush()
        pipe = Popen("kprove -v --debug --default-claim-type all-path --z3-impl-timeout 500 bound.k", shell=True, stdout=PIPE, stderr=PIPE)
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
    find_mev_cdp(PROGRAM, "maker_mev.out", 155042, 155042)

if __name__ == '__main__':
    main()
