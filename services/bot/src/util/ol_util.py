import os
import re
from typing import AnyStr, Dict


def is_slow_wallet(address: AnyStr) -> Dict:
    """
    Checks if a given address is a 'slow' wallet.

    :param address: the address to check

    :return: message: Possible return values:
      - Error > Unvalid address
      - Succes > Account is slow wallet
      - Error > No response from chain
      - Error > Error, cannot find account state for <address>
      - Error > Error, account is not a slow wallet
    """
    
    # check if valid type is passed
    if type(address) != str:
        return {"status": "Error", "message": "Unvalid address"}

    # check if the address is valid via regex
    regex_out = re.search("[a-fA-F0-9]{32}$", address)
    if not regex_out:
        return {"status": "Error", "message": "Unvalid address"}
    
    # check if the address is in fact existing on-chain
    with os.popen(f"ol -a {address} query -u") as f:
        for line in f.readlines():
            splitted = line.split()
            if splitted[2].isnumeric():
                return {"status": "Success", "message": "Account is slow wallet"}
            else:
                return {
                    "status": "Error", 
                    "message": line\
                        .replace('\x1b[0m\x1b[0m\x1b[1m\x1b[36mUNLOCKED BALANCE\x1b[0m ', '')\
                        .replace('\n', '')\
                        .replace('UNLOCKED BALANCE ', '')
                    }
    
    return {"status": "Error", "message": "No response from chain"}


# if __name__ == "__main__":
#     test_list = [
#         "5F8AC83A9B3BF2EFF20A6C16CD05C111", # basic wallet >> SLOW
#         "2BFD96D8A674A360B733D16C65728D72", # validator wallet >> SLOW
#         "1367B68C86CB27FA7215D9F75A26EB8F", # community wallet
#         "5335039ab7908dc38d328685dc3b9141", # miner wallet
#         "7e56b29cb23a49368be593e5cfc9712e", # validator wallet >> SLOW
#         "82a1097c4a173e7941e2c34b4cbf15b4", # miner wallet
#         "",                                 # empty param
#         "19E966BFA4B32CE9B7E23721B37B96D2", # community wallet
#         "cd0fa23141e9e5e348b33c5da51f211d", # miner wallet
#         "bla",                              # Bad address
#         "4be425e5306776a0bd9e2db152b856e6", # miner wallet >> SLOW
#         None,                               # None
#         1,                                  # numeric value
#     ]

#     for addr in test_list:
#         print(f"{is_slow_wallet(addr)}")
    