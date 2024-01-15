"""This file defines mcprotocol constant.
"""
from typing import Tuple

#PLC definetion
Q_SERIES    = "Q"
L_SERIES    = "L"
QnA_SERIES  = "QnA"
iQL_SERIES  = "iQ-L"
iQR_SERIES  = "iQ-R"

#communication type
COMMTYPE_BINARY = "binary"
COMMTYPE_ASCII  = "ascii"

class DeviceCodeError(Exception):
    """devicecode error. Device is not exsist.

    Attributes:
        plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 
        devicename(str):    devicename. (ex: "Q", "P", both of them does not support mcprotocol.)

    """
    def __init__(self, plctype, devicename) -> None:
        ...
    def __str__(self) -> str:
        ...

class DeviceConstants:
    """This class defines mc protocol deveice constatnt.

    Attributes:
        D_DEVICE(int):  D devide code (0xA8)

    """
    #These device supports all series
    SM_DEVICE = 0x91
    SD_DEVICE = 0xA9
    X_DEVICE  = 0x9C
    Y_DEVICE  = 0x9D
    M_DEVICE  = 0x90
    L_DEVICE  = 0x92
    F_DEVICE  = 0x93
    V_DEVICE  = 0x94
    B_DEVICE  = 0xA0
    D_DEVICE  = 0xA8
    W_DEVICE  = 0xB4
    TS_DEVICE = 0xC1
    TC_DEVICE = 0xC0
    TN_DEVICE = 0xC2
    SS_DEVICE = 0xC7
    SC_DEVICE = 0xC6
    SN_DEVICE = 0xC8
    CS_DEVICE = 0xC4
    CC_DEVICE = 0xC3
    CN_DEVICE = 0xC5
    SB_DEVICE = 0xA1
    SW_DEVICE = 0xB5
    DX_DEVICE = 0xA2
    DY_DEVICE = 0xA3
    R_DEVICE  = 0xAF
    ZR_DEVICE = 0xB0

    #These device supports only "iQ-R" series
    LTS_DEVICE  = 0x51
    LTC_DEVICE  = 0x50
    LTN_DEVICE  = 0x52
    LSTS_DEVICE = 0x59
    LSTC_DEVICE = 0x58
    LSTN_DEVICE = 0x5A
    LCS_DEVICE  = 0x55
    LCC_DEVICE  = 0x54
    LCN_DEVICE  = 0x56
    LZ_DEVICE   = 0x62
    RD_DEVICE   = 0x2C

    BIT_DEVICE  = "bit"
    WORD_DEVICE = "word"
    DWORD_DEVICE= "dword"

    
    def __init__(self) -> None:
        """Constructor
        """
        ...
    
    @staticmethod
    def get_binary_devicecode(plctype, devicename) -> Tuple[int, int]:
        """Static method that returns devicecode from device name.

        Args:
            plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            devicename(str):    Device name. (ex: "D", "X", "Y")

        Returns:
            devicecode(int):    Device code defined mc protocol (ex: "D" → 0xA8)
            Base number:        Base number for each device name
        
        """
        ...

    @staticmethod
    def get_ascii_devicecode(plctype, devicename) -> Tuple[str, int]:
        """Static method that returns devicecode from device name.

        Args:
            plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            devicename(str):    Device name. (ex: "D", "X", "Y")

        Returns:
            devicecode(int):    Device code defined mc protocol (ex: "D" → "D*")
            Base number:        Base number for each device name
        
        """
        ...

    @staticmethod
    def get_devicetype(plctype, devicename) -> DeviceConstants:
        """Static method that returns device type "bit" or "wrod" type.

        Args:
            plctype(str):       PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
            devicename(str):    Device name. (ex: "D", "X", "Y")

        Returns:
            devicetyoe(str):    Device type. "bit" or "word"
        
        """
        ...
