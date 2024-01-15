"""This file implements mcprotocol 3E type communication.
"""

import re
import time
import usocket
import struct
import binascii
from . import mcprotocolerror
from . import mcprotocolconst as const

def isascii(text):
    """check text is all ascii character.
    Python 3.6 does not support str.isascii()
    """
    return all(ord(c) < 128 for c in text)

def twos_comp(val, sfmt="h"):
    """compute the 2's complement of int value val
    """
    if sfmt =="c":
        bit = 8
    elif sfmt =="h":
        bit = 16
    elif sfmt== "l":
        bit = 32
    else:
        raise ValueError("cannnot calculate 2's complement")
    if (val & (1 << (bit - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
        val = val - (1 << bit)        # compute negative value
    return val  

def get_device_number(device):
    """Extract device number.

    Ex: "D1000" → "1000"
        "X0x1A" → "0x1A
    """
    device_num = re.search(r"\d.*", device)
    if device_num is None:
        raise ValueError("Invalid device number, {}".format(device))
    else:
        device_num_str = device_num.group(0)
    return device_num_str


class CommTypeError(Exception):
    """Communication type error. Communication type must be "binary" or "ascii"

    """
    def __init__(self):
        pass

    def __str__(self):
        return "communication type must be \"binary\" or \"ascii\""

class PLCTypeError(Exception):
    """PLC type error. PLC type must be"Q", "L", "QnA", "iQ-L", "iQ-R"

    """
    def __init__(self):
        pass

    def __str__(self):
        return "plctype must be \"Q\", \"L\", \"QnA\" \"iQ-L\" or \"iQ-R\""

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
    plctype         = const.Q_SERIES
    commtype        = const.COMMTYPE_BINARY
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


    def __init__(self, plctype ="Q"):
        """Constructor

        """
        self._set_plctype(plctype)
    
    def _set_debug(self, debug=False):
        """Turn on debug mode
        """
        self._debug = debug

    def connect(self, host, port):
        """Connect to PLC

        Args:
            host (str):       hostname/ip to connect PLC
            port (int):     port number of connect PLC   
            timeout (float):  timeout second in communication

        """
        self._host = host
        self._port = port
        try:
            ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)[0]
            # ret [(family, type, proto, cannoname, socketaddr:bytes)], see p26
        except Exception as ex:
            print("connect() error")
            raise ex
        self._sock = usocket.socket(ai[0], usocket.SOCK_STREAM)
        self._sock.settimeout(self.soc_timeout)
        self._sock.connect(ai[-1])
        self._is_connected = True

    def close(self):
        """Close connection

        """
        self._sock.close()
        self._is_connected = False

    def _send(self, send_data):
        """send mc protorocl data 

        Args: 
            send_data(bytes): mc protocol data
        
        """
        if self._is_connected:
            if self._debug:
                print(binascii.hexlify(send_data))
            self._sock.send(send_data)
        else:
            raise Exception("socket is not connected. Please use connect method")

    def _recv(self):
        """recieve mc protocol data

        Returns:
            recv
        """
        recv = self._sock.recv(self._SOCKBUFSIZE)
        return recv

    def _set_plctype(self, plctype):
        """Check PLC type. If plctype is vaild, set self.commtype.

        Args:
            plctype(str):      PLC type. "Q", "L", "QnA", "iQ-L", "iQ-R", 

        """
        if plctype == "Q":
            self.plctype = const.Q_SERIES
        elif plctype == "L":
            self.plctype = const.L_SERIES
        elif plctype == "QnA":
            self.plctype = const.QnA_SERIES
        elif plctype == "iQ-L":
            self.plctype = const.iQL_SERIES
        elif plctype == "iQ-R":
            self.plctype = const.iQR_SERIES
        else:
            raise PLCTypeError()

    def _set_commtype(self, commtype):
        """Check communication type. If commtype is vaild, set self.commtype.

        Args:
            commtype(str):      communication type. "binary" or "ascii". (Default: "binary") 

        """
        if commtype == "binary":
            self.commtype = const.COMMTYPE_BINARY
            self._wordsize = 2
        elif commtype == "ascii":
            self.commtype = const.COMMTYPE_ASCII
            self._wordsize = 4
        else:
            raise CommTypeError()

    def _get_answerdata_index(self):
        """Get answer data index from return data byte.
        """
        if self.commtype == const.COMMTYPE_BINARY:
            return 11
        else:
            return 22

    def _get_answerstatus_index(self):
        """Get cmd status index from return data byte.
        """
        if self.commtype == const.COMMTYPE_BINARY:
            return 9
        else:
            return 18

    def setaccessopt(self, commtype=None, network=None, 
                     pc=None, dest_moduleio=None, 
                     dest_modulesta=None, timer_sec=None):
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
        if commtype:
            self._set_commtype(commtype)
        if network:
            try:
                network.to_bytes(1, "little")
                self.network = network
            except:
                raise ValueError("network must be 0 <= network <= 255")
        if pc:
            try:
                pc.to_bytes(1, "little")
                self.pc = pc
            except:
                raise ValueError("pc must be 0 <= pc <= 255") 
        if dest_moduleio:
            try:
                dest_moduleio.to_bytes(2, "little")
                self.dest_moduleio = dest_moduleio
            except:
                raise ValueError("dest_moduleio must be 0 <= dest_moduleio <= 65535") 
        if dest_modulesta:
            try:
                dest_modulesta.to_bytes(1, "little")
                self.dest_modulesta = dest_modulesta
            except:
                raise ValueError("dest_modulesta must be 0 <= dest_modulesta <= 255") 
        if timer_sec:
            try:
                timer_250msec = 4 * timer_sec
                timer_250msec.to_bytes(2, "little")
                self.timer = timer_250msec
                self.soc_timeout = timer_sec + 1
                if self._is_connected:
                    self._sock.settimeout(self.soc_timeout)
            except:
                raise ValueError("timer_sec must be 0 <= timer_sec <= 16383, / sec") 
        return None
    
    def _make_senddata(self, requestdata):
        """Makes send mc protorocl data.

        Args:
            requestdata(bytes): mc protocol request data. 
                                data must be converted according to self.commtype

        Returns:
            mc_data(bytes):     send mc protorocl data

        """
        mc_data = bytes()
        # subheader is big endian
        if self.commtype == const.COMMTYPE_BINARY:
             mc_data += self.subheader.to_bytes(2, "big")
        else:
            mc_data += format(self.subheader, "x").ljust(4, "0").upper().encode()
        mc_data += self._encode(self.network, "B")
        mc_data += self._encode(self.pc, "B")
        mc_data += self._encode(self.dest_moduleio, "H")
        mc_data += self._encode(self.dest_modulesta, "B")
        #add self.timer size
        mc_data += self._encode(self._wordsize + len(requestdata), "H")
        mc_data += self._encode(self.timer, "H")
        mc_data += requestdata
        return mc_data

    def _mk_cmd(self, cmd, subcmd):
        """make mc protocol cmd and subcmd data

        Args:
            cmd(int):       cmd code
            subcmd(int):    subcmd code

        Returns:
            cmd_data(bytes):cmd data

        """
        cmd_data = bytes()
        cmd_data += self._encode(cmd, "H")
        cmd_data += self._encode(subcmd, "H")
        return cmd_data
    
    def _mk_dev(self, device):
        """make mc protocol device data. (device code and device number)
        
        Args:
            device(str): device. (ex: "D1000", "Y1")

        Returns:
            dev_data(bytes): device data
            
        """
        
        dev_data = bytes()

        devicetype = re.search(r"\D+", device)
        if devicetype is None:
            raise ValueError("Invalid device ")
        else:
            devicetype = devicetype.group(0)      

        if self.commtype == const.COMMTYPE_BINARY:
            devicecode, devicebase = const.DeviceConstants.get_binary_devicecode(self.plctype, devicetype)
            devicenum = int(get_device_number(device), devicebase)
            if self.plctype is const.iQR_SERIES:
                dev_data += devicenum.to_bytes(4, "little")
                dev_data += devicecode.to_bytes(2, "little")
            else:
                dev_data += devicenum.to_bytes(3, "little")
                dev_data += devicecode.to_bytes(1, "little")
        else:
            devicecode, devicebase = const.DeviceConstants.get_ascii_devicecode(self.plctype, devicetype)
            devicenum = str(int(get_device_number(device), devicebase))
            if self.plctype is const.iQR_SERIES:
                dev_data += devicecode.encode()
                dev_data += devicenum.rjust(8, "0").upper().encode()
            else:
                dev_data += devicecode.encode()
                dev_data += devicenum.rjust(6, "0").upper().encode()
        return dev_data

    def _encode(self, value, sfmt="H"):
        """encode mc protocol value data to byte.

        Args: 
            value(int):   readsize, write value, and so on.
            sfmt(str):      b/h/l char(byte)/short/long, cap=unsigned

        Returns:
            value_byte(bytes):  value data
        
        """
        try:
            if self.commtype == const.COMMTYPE_BINARY:
                if sfmt in "bhlBHL":
                    value_byte = struct.pack("<"+sfmt, value)
                else: 
                    raise ValueError(f"_encode wrong sfmt {sfmt}")
            else:
                #check value range by to_bytes
                #convert to unsigned value
                # kwarg signed:bool is not supported on mpy, removed
                if sfmt == "B":
                    value.to_bytes(1, "little")
                    value = value & 0xff
                    value_byte = format(value, "x").rjust(2, "0").upper().encode()
                elif sfmt == "H":
                    value.to_bytes(2, "little")
                    value = value & 0xffff
                    value_byte = format(value, "x").rjust(4, "0").upper().encode()
                elif sfmt == "L":
                    value.to_bytes(4, "little")
                    value = value & 0xffffffff
                    value_byte = format(value, "x").rjust(8, "0").upper().encode()
                else: 
                    raise ValueError(f"_encode missing/wrong sfmt ({sfmt})")
        except Exception as ex:
            print("_encode error", type(ex))
            raise ex
        return value_byte

    def _decode(self, byte, sfmt="H"):
        """decode byte to value

        Args: 
            byte(bytes):    readsize, write value, and so on.
            sfmt(str):      b/h/l char(byte)/short/long, cap=unsigned

        Returns:
            value_data(int):  value data
        
        """
        try:
            if self.commtype == const.COMMTYPE_BINARY:
                if sfmt in "bhlBHL":
                    value = struct.unpack("<"+sfmt, byte)[0]
                else: 
                    raise ValueError(f"_decode wrong sfmt {sfmt}")
            else:
                value = int(byte.decode(), 16)
                if sfmt in "bhl":
                    value = twos_comp(value, sfmt)
        except Exception as ex:
            print("_decode error", type(ex))
            raise ex
        return value
        
    def _check_cmdanswer(self, recv):
        """check cmd answer. If answer status is not 0, raise error according to answer  

        """
        answerstatus_index = self._get_answerstatus_index()
        answerstatus = self._decode(recv[answerstatus_index:answerstatus_index+self._wordsize], "H")
        mcprotocolerror.check_mcprotocol_error(answerstatus)
        return None

    def batchread_wordunits(self, headdevice, readsize):
        """batch read in word units.

        Args:
            headdevice(str):    Read head device. (ex: "D1000")
            readsize(int):      Number of read device points

        Returns:
            wordunits_values(list[int]):  word units value list

        """
        cmd = 0x0401
        if self.plctype == const.iQR_SERIES:
            subcmd = 0x0002
        else:
            subcmd = 0x0000
        
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._mk_dev(headdevice)
        req += self._encode(readsize)
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)

        word_values = []
        idx = self._get_answerdata_index()
        for _ in range(readsize):
            wordvalue = self._decode(recv[idx:idx+self._wordsize], sfmt="h")
            word_values.append(wordvalue)
            idx += self._wordsize
        return word_values

    def batchread_bitunits(self, headdevice, readsize):
        """batch read in bit units.

        Args:
            headdevice(str):    Read head device. (ex: "X1")
            size(int):          Number of read device points

        Returns:
            bitunits_values(list[int]):  bit units value(0 or 1) list

        """
        cmd = 0x0401
        if self.plctype == const.iQR_SERIES:
            subcmd = 0x0003
        else:
            subcmd = 0x0001
        
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._mk_dev(headdevice)
        req += self._encode(readsize)
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)

        bit_values = []
        if self.commtype == const.COMMTYPE_BINARY:
            for i in range(readsize):
                idx = i//2 + self._get_answerdata_index()
                value = int.from_bytes(recv[idx:idx+1], "little")
                #if i//2==0, bit value is 4th bit
                if(i%2==0):
                    bitvalue = 1 if value & (1<<4) else 0
                else:
                    bitvalue = 1 if value & (1<<0) else 0
                bit_values.append(bitvalue)
        else:
            idx = self._get_answerdata_index()
            byte_range = 1
            for i in range(readsize):
                bitvalue = int(recv[idx:idx+byte_range].decode())
                bit_values.append(bitvalue)
                idx += byte_range
        return bit_values

    def batchwrite_wordunits(self, headdevice, values):
        """batch write in word units.

        Args:
            headdevice(str):    Write head device. (ex: "D1000")
            values(list[int]):  Write values.

        """
        write_size = len(values)

        cmd = 0x1401
        if self.plctype == const.iQR_SERIES:
            subcmd = 0x0002
        else:
            subcmd = 0x0000
        
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._mk_dev(headdevice)
        req += self._encode(write_size)
        for value in values:
            req += self._encode(value, sfmt="h")
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)

        return None

    def batchwrite_bitunits(self, headdevice, values):
        """batch read in bit units.

        Args:
            headdevice(str):    Write head device. (ex: "X10")
            values(list[int]):  Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.

        """
        write_size = len(values)
        #check values
        for value in values:
            if not (value == 0 or value == 1): 
                raise ValueError("Each value must be 0 or 1. 0 is OFF, 1 is ON.")

        cmd = 0x1401
        if self.plctype == const.iQR_SERIES:
            subcmd = 0x0003
        else:
            subcmd = 0x0001
        
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._mk_dev(headdevice)
        req += self._encode(write_size)
        if self.commtype == const.COMMTYPE_BINARY:
            #evary value is 0 or 1.
            #Even index's value turns on or off 4th bit, odd index's value turns on or off 0th bit.
            #First, create send data list. Length must be ceil of len(values).
            bit_data = [0 for _ in range((len(values) + 1)//2)]
            for index, value in enumerate(values):
                #calc which index data should be turns on.
                value_index = index//2
                #calc which bit should be turns on.
                bit_index = 4 if index%2 == 0 else 0
                #turns on or off value of 4th or 0th bit, depends on value
                bit_value = value << bit_index
                #Take or of send data
                bit_data[value_index] |= bit_value
            req += bytes(bit_data)
        else:
            for value in values:
                req += str(value).encode()
        send_data = self._make_senddata(req)
                    
        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)

        return None

    def _randomread(self, word_devices, dword_devices):
        """read word units and dword units randomly.
        Moniter condition does not support.

        Args:
            word_devices(list[str]):    Read device word units. (ex: ["D1000", "D1010"])
            dword_devices(list[str]):   Read device dword units. (ex: ["D1000", "D1012"])

        Returns:
            word_values(list[int]):     word units value list
            dword_values(list[int]):    dword units value list

        """
        cmd = 0x0403
        if self.plctype == const.iQR_SERIES:
            subcmd = 0x0002
        else:
            subcmd = 0x0000

        word_size = len(word_devices)
        dword_size = len(dword_devices)
        
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(word_size, sfmt="B")
        req += self._encode(dword_size, sfmt="B")
        for word_device in word_devices:
            req += self._mk_dev(word_device)
        for dword_device in dword_devices:
            req += self._mk_dev(dword_device)        
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)
        idx = self._get_answerdata_index()
        return recv, idx

    def randomread(self, word_devices, dword_devices):
        recv, idx = self._randomread(word_devices, dword_devices)
        word_values= []
        dword_values= []
        for word_device in word_devices:
            wordvalue = self._decode(recv[idx:idx+self._wordsize], sfmt="h")
            word_values.append(wordvalue)
            idx += self._wordsize
        for dword_device in dword_devices:
            dwordvalue = self._decode(recv[idx:idx+self._wordsize*2], sfmt="l")
            dword_values.append(dwordvalue)
            idx += self._wordsize*2
        return word_values, dword_values

    def randomread_bytes(self, word_devices, dword_devices):
        recv, idx = self._randomread(word_devices, dword_devices)
        word_values= []
        dword_values= []
        for word_device in word_devices:
            wordvalue = recv[idx:idx+self._wordsize]
            word_values.append(wordvalue)
            idx += self._wordsize
        for dword_device in dword_devices:
            dwordvalue = recv[idx:idx+self._wordsize*2]
            dword_values.append(dwordvalue)
            idx += self._wordsize*2
        return word_values, dword_values

    def randomwrite(self, word_devices, word_values,
                    dword_devices, dword_values):
        """write word units and dword units randomly.

        Args:
            word_devices(list[str]):    Write word devices. (ex: ["D1000", "D1020"])
            word_values(list[int]):     Values for each word devices. (ex: [100, 200])
            dword_devices(list[str]):   Write dword devices. (ex: ["D1000", "D1020"])
            dword_values(list[int]):    Values for each dword devices. (ex: [100, 200])

        """
        if len(word_devices) != len(word_values):
            raise ValueError("word_devices and word_values must be same length")
        if len(dword_devices) != len(dword_values):
            raise ValueError("dword_devices and dword_values must be same length")
            
        word_size = len(word_devices)
        dword_size = len(dword_devices)

        cmd = 0x1402
        if self.plctype == const.iQR_SERIES:
            subcmd = 0x0002
        else:
            subcmd = 0x0000
        
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(word_size, sfmt="B")
        req += self._encode(dword_size, sfmt="B")
        for word_device, word_value in zip(word_devices, word_values):
            req += self._mk_dev(word_device)
            req += self._encode(word_value, sfmt="h")
        for dword_device, dword_value in zip(dword_devices, dword_values):
            req += self._mk_dev(dword_device)   
            req += self._encode(dword_value, sfmt="l")     
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)
        return None

    def randomwrite_bitunits(self, bit_devices, values):
        """write bit units randomly.

        Args:
            bit_devices(list[str]):    Write bit devices. (ex: ["X10", "X20"])
            values(list[int]):         Write values. each value must be 0 or 1. 0 is OFF, 1 is ON.

        """
        if len(bit_devices) != len(values):
            raise ValueError("bit_devices and values must be same length")
        write_size = len(values)
        #check values
        for value in values:
            if not (value == 0 or value == 1): 
                raise ValueError("Each value must be 0 or 1. 0 is OFF, 1 is ON.")

        cmd = 0x1402
        if self.plctype == const.iQR_SERIES:
            subcmd = 0x0003
        else:
            subcmd = 0x0001
        
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(write_size, sfmt="B")
        for bit_device, value in zip(bit_devices, values):
            req += self._mk_dev(bit_device)
            #byte value for iQ-R requires 2 byte data
            if self.plctype == const.iQR_SERIES:
                req += self._encode(value, sfmt="h")
            else:
                req += self._encode(value, sfmt="b")
        send_data = self._make_senddata(req)
                    
        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)

        return None

    def remote_run(self, clear_mode, force_exec=False):
        """Run PLC

        Args:
            clear_mode(int):     Clear mode. 0: does not clear. 1: clear except latch device. 2: clear all.
            force_exec(bool):    Force to execute if PLC is operated remotely by other device.

        """
        if not (clear_mode == 0 or  clear_mode == 1 or clear_mode == 2):
            raise ValueError("clear_device must be 0, 1 or 2. 0: does not clear. 1: clear except latch device. 2: clear all.")
        if not (force_exec is True or force_exec is False):
            raise ValueError("force_exec must be True or False")

        cmd = 0x1001
        subcmd = 0x0000

        if force_exec:
            mode = 0x0003
        else:
            mode = 0x0001
          
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(mode, sfmt="H")
        req += self._encode(clear_mode, sfmt="B")
        req += self._encode(0, sfmt="B")
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)
        return None

    def remote_stop(self):
        """ Stop remotely.

        """
        cmd = 0x1002
        subcmd = 0x0000

        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(0x0001, sfmt="H") #fixed value
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)
        return None

    def remote_pause(self, force_exec=False):
        """pause PLC remotely.

        Args:
            force_exec(bool):    Force to execute if PLC is operated remotely by other device.

        """
        if not (force_exec is True or force_exec is False):
            raise ValueError("force_exec must be True or False")

        cmd = 0x1003
        subcmd = 0x0000

        if force_exec:
            mode = 0x0003
        else:
            mode = 0x0001
          
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(mode, sfmt="H")
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)
        return None

    def remote_latchclear(self):
        """Clear latch remotely.
        PLC must be stop when use this cmd.
        """

        cmd = 0x1005
        subcmd = 0x0000

        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(0x0001, sfmt="H") #fixed value 
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)

        return None

    def remote_reset(self):
        """Reset remotely.
        PLC must be stop when use this cmd.
        
        """

        cmd = 0x1006
        subcmd = 0x0000

        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(0x0001, sfmt="H") #fixed value
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        #set time out 1 seconds. Because remote reset may not return data since clone socket
        try:
            self._sock.settimeout(1)
            recv = self._recv()
            self._check_cmdanswer(recv)
        except:
            self._is_connected = False
            # after wait 1 sec
            # try reconnect
            time.sleep(1)
            self.connect(self._host, self._port)
        return None

    def read_cputype(self):
        """Read CPU type

        Returns:
            CPU type(str):      CPU type
            CPU code(str):      CPU code (4 length number)

        """

        cmd = 0x0101
        subcmd = 0x0000

        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)
        idx = self._get_answerdata_index()
        cpu_name_length = 16
        if self.commtype == const.COMMTYPE_BINARY:
            cpu_type = recv[idx:idx+cpu_name_length].decode()
            cpu_type = cpu_type.replace("\x20", "")
            cpu_code = int.from_bytes(recv[idx+cpu_name_length:], "little")
            cpu_code = format(cpu_code, "x").rjust(4, "0")
        else:
            cpu_type = recv[idx:idx+cpu_name_length].decode()
            cpu_type = cpu_type.replace("\x20", "")
            cpu_code = recv[idx+cpu_name_length:].decode()
        return cpu_type, cpu_code

    def remote_unlock(self, password="", request_input=False):
        """Unlock PLC by inputting password.

        Args:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """
        if request_input:
            password = input("Please enter password\n")
        if isascii(password) is False:
            raise ValueError("password must be only ascii code")
        if self.plctype is const.iQR_SERIES:
            if not (6 <= len(password) <= 32):
                raise ValueError("password length must be from 6 to 32")
        else:
            if not (4 == len(password)):
                raise ValueError("password length must be 4")


        cmd = 0x1630
        subcmd = 0x0000
        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(len(password), sfmt="H") 
        req += password.encode()

        send_data = self._make_senddata(req)

        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)
        return None

    def remote_lock(self, password="", request_input=False):
        """Lock PLC by inputting password.

        Args:
            password(str):          Remote password
            request_input(bool):    If true, require inputting password.
                                    If false, use password.
        """
        if request_input:
            password = input("Please enter password\n")
        if isascii(password) is False:
            raise ValueError("password must be only ascii code")
        if self.plctype is const.iQR_SERIES:
            if not (6 <= len(password) <= 32):
                raise ValueError("password length must be from 6 to 32")
        else:
            if not (4 == len(password)):
                raise ValueError("password length must be 4")

        cmd = 0x1631
        subcmd = 0x0000

        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(len(password), sfmt="H") 
        req += password.encode()

        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)
        return None

    def echo_test(self, echo_data):
        """Do echo test.
        Send data and answer data should be same.

        Args:
            echo_data(str):     send data to PLC

        Returns:
            answer_len(int):    answer data length from PLC
            answer_data(str):   answer data from PLC

        """
        if echo_data.isalnum() is False:
            raise ValueError("echo_data must be only alphabet or digit code")
        if not ( 1 <= len(echo_data) <= 960):
            raise ValueError("echo_data length must be from 1 to 960")

        cmd = 0x0619
        subcmd = 0x0000

        req = bytes()
        req += self._mk_cmd(cmd, subcmd)
        req += self._encode(len(echo_data), sfmt="H") 
        req += echo_data.encode()

        send_data = self._make_senddata(req)

        #send mc data
        self._send(send_data)
        #reciev mc data
        recv = self._recv()
        self._check_cmdanswer(recv)

        idx = self._get_answerdata_index()

        answer_len = self._decode(recv[idx:idx+self._wordsize], sfmt="H") 
        answer = recv[idx+self._wordsize:].decode()
        return answer_len, answer