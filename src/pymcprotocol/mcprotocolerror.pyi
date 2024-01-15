"""This file is collection of mcprotocol error.

"""

class MCProtocolError(Exception):
    """devicecode error. Device is not exsist.

    Attributes:
        plctype(str):       PLC type. "Q", "L" or "iQ"
        devicename(str):    devicename. (ex: "Q", "P", both of them does not support mcprotocol.)

    """
    def __init__(self, errorcode) -> None:
        ...
    def __str__(self) -> str:
        ...

class UnsupportedComandError(Exception):
    """This command is not supported by the module you connected.  

    """
    def __init__(self) -> None:
        ...
    def __str__(self) -> str:
        ...

    
def check_mcprotocol_error(status) -> None:
    ...

