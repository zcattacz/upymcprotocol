"""This file implements mcprotocol 3E type communication.
"""
from typing import Any, Union, Tuple

def isascii(text) -> bool:
    """check text is all ascii character.
    Python 3.6 does not support str.isascii()
    """
    ...

def twos_comp(val, sfmt="h") -> int:
    """compute the 2's complement of int value val
    """
    ...

def get_device_number(device) -> str:
    """Extract device number.

    Ex: "D1000" → "1000"
        "X0x1A" → "0x1A
    """
    ...

class CommTypeError(Exception):
    """Communication type error. Communication type must be "binary" or "ascii"

    """
    def __init__(self) -> None:
        ...

    def __str__(self) -> str:
        ...

class PLCTypeError(Exception):
    """PLC type error. PLC type must be"Q", "L", "QnA", "iQ-L", "iQ-R"

    """
    def __init__(self) -> None:
        ...

    def __str__(self) -> str:
        ...

class Type3E:
    """mcprotocol 3E communication class.

    Attributes:
        plctype(str):           connect PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R"
        commtype(str):          communication type. "binary" or "ascii". (Default: "binary") 
        subheader(int):         Subheader for mc protocol
        network(int):           network No. of an access target. (0<= network <= 255)
        pc(int):                network module station No. of an access target. (0<= pc <= 255)
        dest_moduleio(int):     When accessing a multidrop connection station via network, 
                                specify the start input/output number of a multidrop connection source module.
                                the CPU module of the multiple CPU system and redundant system.
        dest_modulesta(int):    accessing a multidrop connection station via network, 
                                specify the station No. of aaccess target module
        timer(int):             time to raise Timeout error(/250msec). default=4(1sec)
                                If PLC elapsed this time, PLC returns Timeout answer.
                                Note: python socket timeout is always set timer+1sec. To recieve Timeout answer.
    """
    plctype: str
    commtype: str
    subheader       = 0x5000
    network         = 0
    pc              = 0xFF
    dest_moduleio   = 0X3FF
    dest_modulesta  = 0X0
    timer           = 4 # MC protocol timeout. 250msec * 4 = 1 sec 
    soc_timeout     = 2 # 2 sec
    _is_connected   = False
    _SOCKBUFSIZE    = 4096
    _wordsize       = 2 #how many byte is required to describe word value 
                        #binary: 2, ascii:4.
    _debug          = False


    def __init__(self, plctype ="Q") -> None:
        """Constructor

        """
        ...
    
    def _set_debug(self, debug=False) -> None:
        """Turn on debug mode
        """
        ...

    def connect(self, host, port) -> None:
        """Connect to PLC

        Args:
            host (str):       hostname/ip to connect PLC
            port (int):     port number of connect PLC   
            timeout (float):  timeout second in communication

        """
        ...

    def close(self) -> None:
        """Close connection

        """
        ...

    def _send(self, send_data) -> None:
        """send mc protorocl data 

        Args: 
            send_data(bytes): mc protocol data
        
        """
        ...

    def _recv(self) -> bytes:
        """recieve mc protocol data

        Returns:
            recv
        """
        ...

    def _set_plctype(self, plctype) -> None:
        """Check PLC type. If plctype is vaild, set self.commtype.

        Args:
            plctype(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 

        """

    def _set_commtype(self, commtype) -> None:
        """Check communication type. If commtype is vaild, set self.commtype.

        Args:
            commtype(str):      communication type. "binary" or "ascii". (Default: "binary") 

        """

    def _get_answerdata_index(self) -> int:
        """Get answer data index from return data byte.
        """

    def _get_answerstatus_index(self) -> int:
        """Get cmd status index from return data byte.
        """

    def setaccessopt(self, commtype=None, network=None, 
                     pc=None, dest_moduleio=None, 
                     dest_modulesta=None, timer_sec=None) -> None:
        """Set mc protocol access option.

        Args:
            commtype(str):          communication type. "binary" or "ascii". (Default: "binary") 
            network(int):           network No. of an access target. (0<= network <= 255)
            pc(int):                network module station No. of an access target. (0<= pc <= 255)
            dest_moduleio(int):     When accessing a multidrop connection station via network, 
                                    specify the start input/output number of a multidrop connection source module.
                                    the CPU module of the multiple CPU system and redundant system.
            dest_modulesta(int):    accessing a multidrop connection station via network, 
                                    specify the station No. of aaccess target module
            timer_sec(int):         Time out to return Timeout Error from PLC. 
                                    MC protocol time is per 250msec, but for ease, setaccessopt requires per sec.
                                    Socket time out is set timer_sec + 1 sec.

        """
        ...
    
    def _make_senddata(self, requestdata) -> bytes:
        """Makes send mc protorocl data.

        Args:
            requestdata(bytes): mc protocol request data. 
                                data must be converted according to self.commtype

        Returns:
            mc_data(bytes):     send mc protorocl data

        """
        ...

    def _mk_cmd(self, cmd, subcmd) -> bytes:
        """make mc protocol cmd and subcmd data

        Args:
            cmd(int):       cmd code
            subcmd(int):    subcmd code

        Returns:
            cmd_data(bytes):cmd data

        """
        ...
    
    def _mk_dev(self, device) -> bytes:
        """make mc protocol device data. (device code and device number)
        
        Args:
            device(str): device. (ex: "D1000", "Y1")

        Returns:
            dev_data(bytes): device data
            
        """
        ...

    def _encode(self, value, sfmt="H") -> bytes:
        """encode mc protocol value data to byte.

        Args: 
            value(int):   readsize, write value, and so on.
            sfmt(str):      b/h/l char(byte)/short/long, cap=unsigned

        Returns:
            value_byte(bytes):  value data
        
        """
        ...

    def _decode(self, byte, sfmt="H") -> Union[int, float]:
        """decode byte to value

        Args: 
            byte(bytes):    readsize, write value, and so on.
            sfmt(str):      b/h/l char(byte)/short/long, cap=unsigned

        Returns:
            value_data(int):  value data
        
        """
        ...
        
    def _check_cmdanswer(self, recv) -> None:
        """check cmd answer. If answer status is not 0, raise error according to answer  

        """
        ...

    def batchread_wordunits(self, headdevice, readsize) -> list[Union[int, float]]:
        """batch read in word units.

        Args:
            headdevice(str):    Read head device. (ex: "D1000")
            readsize(int):      Number of read device points

        Returns:
            wordunits_values(list[int]):  word units value list

        """
        ...

    def batchread_bitunits(self, headdevice, readsize) -> list[int]:
        """batch read in bit units.

        Args:
            headdevice(str):    Read head device. (ex: "X1")
            size(int):          Number of read device points

        Returns:
            bitunits_values(list[int]):  bit units value(0 or 1) list

        """
        ...

    def batchwrite_wordunits(self, headdevice:str, values:list[int]) -> None:
        """batch write in word units.

        Args:
            headdevice(str):    Write head device. (ex: "D1000")
            values(list[int]):  Write values.

        """
        ...

    def batchwrite_bitunits(self, headdevice:str, values:list[int])-> None:
        """batch read in bit units.

        Args:
            headdevice(str):    Write head device. (ex: "X10")
            values(list[int]):  Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.

        """
        ...

    def _randomread(self, word_devices, dword_devices) -> Tuple[bytes, int]:
        """read word units and dword units randomly.
        Moniter condition does not support.

        Args:
            word_devices(list[str]):    Read device word units. (ex: ["D1000", "D1010"])
            dword_devices(list[str]):   Read device dword units. (ex: ["D1000", "D1012"])

        Returns:
            word_values(list[int]):     word units value list
            dword_values(list[int]):    dword units value list

        """
        ...

    def randomread(self, word_devices, dword_devices) -> Tuple[list[Union[int,float]], list[Union[int,float]]]:
        ...

    def randomread_bytes(self, word_devices, dword_devices) -> Tuple[list[bytes], list[bytes]]:
        ...

    def randomwrite(self, word_devices, word_values,
                    dword_devices, dword_values) -> None:
        """write word units and dword units randomly.

        Args:
            word_devices(list[str]):    Write word devices. (ex: ["D1000", "D1020"])
            word_values(list[int]):     Values for each word devices. (ex: [100, 200])
            dword_devices(list[str]):   Write dword devices. (ex: ["D1000", "D1020"])
            dword_values(list[int]):    Values for each dword devices. (ex: [100, 200])

        """
        ...

    def randomwrite_bitunits(self, bit_devices, values) -> None:
        """write bit units randomly.

        Args:
            bit_devices(list[str]):    Write bit devices. (ex: ["X10", "X20"])
            values(list[int]):         Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.

        """
        ...

    def remote_run(self, clear_mode, force_exec=False) -> None:
        """Run PLC

        Args:
            clear_mode(int):     Clear mode. 0: does not clear. 1: clear except latch device. 2: clear all.
            force_exec(bool):    Force to execute if PLC is operated remotely by other device.

        """
        ...

    def remote_stop(self) -> None:
        """ Stop remotely.

        """

    def remote_pause(self, force_exec=False) -> None:
        """pause PLC remotely.

        Args:
            force_exec(bool):    Force to execute if PLC is operated remotely by other device.

        """
        ...

    def remote_latchclear(self) -> None:
        """Clear latch remotely.
        PLC must be stop when use this cmd.
        """
        ...

    def remote_reset(self):
        """Reset remotely.
        PLC must be stop when use this cmd.
        
        """
        ...

    def read_cputype(self) -> Tuple[str, str]:
        """Read CPU type

        Returns:
            CPU type(str):      CPU type
            CPU code(str):      CPU code (4 length number)

        """
        ...

    def remote_unlock(self, password="", request_input=False) -> None:
        """Unlock PLC by inputting password.

        Args:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """
        ...

    def remote_lock(self, password="", request_input=False) -> None:
        """Lock PLC by inputting password.

        Args:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """
        ...

    def echo_test(self, echo_data) -> Tuple[int, str]:
        """Do echo test.
        Send data and answer data should be same.

        Args:
            echo_data(str):     send data to PLC

        Returns:
            answer_len(int):    answer data length from PLC
            answer_data(str):   answer data from PLC

        """
        ...
        