from kutils import find_integer_bound

UNISWAP_LOWER_BOUND = "{?S[Uniswap in 0]}:>Int >=Int %d"
UNISWAP_UPPER_BOUND = "{?S[Uniswap in 0]}:>Int <=Int %d"
PROGRAM = """Uniswap in 0 gets 0;
        Uniswap in 1454383474624795085458277788004692202315323288702 gets 0;
        // transaction 0x003c5d067ee03836a4374f4d5c3466e0d8328f62496b5dd1cbdf4d6db6aeacfe
        572342420797838882173629907578269659270010768697 adds 100000000000000000000 tokens and 20000000000000000 eth of liquidity to 1454383474624795085458277788004692202315323288702;
        // transaction 0xd54a6243159e4068cb50aebf4645b117bd6bfd627cf7819734c48bd984d5f4e8
        616870745215506062750269120831072350349526031960 in 0 swaps 295147905179352825856 input for 1454383474624795085458277788004692202315323288702 fee 478923078075;
        // transaction 0x3a2fd182d016977a87d33ecf67e81d930e07f47d623320a41028f5bbf869db32
        368839096625159992408953185476375976377428775247 in 1454383474624795085458277788004692202315323288702 swaps 120443408692820097171972 input for 0 fee 1177002069144;
        // transaction 0x0adb278e7096e67aca0bdb32f9794322a7b8be5835fe21ef0aa012e85b2e77dc
        616870745215506062750269120831072350349526031960 adds 83290999999999977725 tokens and 125401513679990865 eth of liquidity to 1454383474624795085458277788004692202315323288702;
        // transaction 0xb0cece3304dc2563fbb2d17736c751b8b441f04683e529c0a251799b7286f6b8
        368839096625159992408953185476375976377428775247 in 1454383474624795085458277788004692202315323288702 swaps 2419684155471892146710118 input for 0 fee 1008871952048;"""

find_integer_bound(PROGRAM, "uniswap_lower_bound.out", UNISWAP_LOWER_BOUND, 999999999999999999999999999999999)
find_integer_bound(PROGRAM, "uniswap_upper_bound.out", UNISWAP_UPPER_BOUND, 0)