import os
import sys
from subprocess import Popen, PIPE
import re
from pathlib import Path

MAKER_DATA = """
exec(276203969674087029088707267242881295499809928317 opens vault 155042);
exec(276203969674087029088707267242881295499809928317 locks 9051654598458972160 collateral to vault 155042);
exec(276203969674087029088707267242881295499809928317 draws 800000000000000000000 debt from vault 155042);
"""


BLANK_SPEC = """module BOUND
    imports MEV
    rule <k>
            0 in 0 gets 0;
            0 in SAI gets 0;
            %s
            0 bites vault %s;
         => ?X 
     </k>
    <S> ( (Uniswap in 0) |-> 0 (Uniswap in SAI) |-> 0 ) =>?S:Map </S>
    <M> .Set => ?_:Set </M>
    <B> .List => ?_ </B>
    <P> .Map => ?_ </P>
    <V> .Map => ?_ </V>
    ensures ( ({?S[0 in SAI]}:>Int <=Int 0) andBool ?X ==K DONE) orBool (?X ==K FAIL)
endmodule
"""

def find_mev_cdp(program, spec_file, outfile, starting_value, end_value):
    global BLANK_SPEC
    for v in range(starting_value, end_value+1):
        output = ""
        spec = BLANK_SPEC % (program + MAKER_DATA, v)
        Path(os.path.dirname(spec_file)).mkdir(parents=True, exist_ok=True)
        open(spec_file, "w").write(spec)
        print("Starting proof..." + str(v))
        sys.stdout.flush()
        pipe = Popen("kprove -v --debug --default-claim-type all-path --z3-impl-timeout 500 " + spec_file, shell=True, stdout=PIPE, stderr=PIPE)
        output = pipe.stdout.read() + pipe.stderr.read()
        output = str(output, "utf-8")
        print(output)
        if "#True" not in output:
            print("MEV FOUND!")
            print("Writing MEV configuration to", outfile, "...")
            open(outfile, "w").write(output)
            return

def main():
    PROGRAM = open('data/' + sys.argv[1]).read()
    spec_file = sys.argv[1]+'/bound.k'
    outfile = 'output/'+sys.argv[1]+'.out'
    find_mev_cdp(PROGRAM, spec_file, outfile, 155042, 155042)

if __name__ == '__main__':
    main()
