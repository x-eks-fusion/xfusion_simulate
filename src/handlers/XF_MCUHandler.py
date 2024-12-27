import struct
import json

from handlers.XF_GPIOHandler import GPIOHandler
from handlers.XF_PWMHandler import PWMHandler
from handlers.XF_TimerHandler import TimerHandler
from handlers.XF_UARTHandler import UARTHandler
from handlers.XF_I2CHandler import I2CHandler
from handlers.XF_SPIHandler import SPIHandler
from handlers.XF_ADCHandler import ADCHandler
from handlers.XF_DACHandler import DACHandler


class MCUHandler:

    def __init__(self, server):
        self.server = server
        self.handlers = {}

    @staticmethod
    def packTLV(type_value, data):
        # 确保 type_value 是 4 个字节，data 是字节对象
        if not isinstance(type_value, int) or not (0 <= type_value < (1 << 32)):
            raise ValueError("Type must be an integer within 4 bytes range.")
        if isinstance(data, str):
            data_bytes = data.encode()  # 如果输入是字符串，则编码成字节
        elif isinstance(data, int):
            data_bytes = data.to_bytes(
                (data.bit_length() + 7) // 8 or 1, byteorder='little', signed=False
            )
        else:
            data_bytes = data
        length = len(data_bytes)

        # 构建 TLV 格式的二进制流
        tlv = struct.pack('<I Q', type_value, length) + data_bytes

        return tlv

    def handle(self, client_socket, msg_id, value):
        self.client_socket = client_socket
        self.msg_id = msg_id
        self.value = value
        print(f"msg_id: {msg_id}, value: {value}")
        if msg_id == 0:
            self.configHandler()
        elif msg_id == 1:
            self.getHandler()
        elif msg_id == 2:
            self.isrHandler()
        elif msg_id > 0x1000000:
            handler = self.getHandlerByID(msg_id)
            if handler:
                handler.reciveHandler(value)
            else:
                raise ValueError(
                    f"Handler for message type {msg_id} not found")
        else:
            raise ValueError(f"Handler for message type {msg_id} not found")

    def configHandler(self):
        response = json.loads(self.value.decode())
        handler = self.getHandlerByID(response["id"])
        if handler:
            handler.configHandler(response)

    def getHandler(self):
        response = json.loads(self.value.decode())
        handler = self.getHandlerByID(response["id"])

        if handler:
            send_value = handler.getHandler(response)
            tlv = self.packTLV(self.msg_id, send_value)
            self.client_socket.send(tlv)

    def isrHandler(self):
        print("isrHandler")

    def getHandlerByID(self, id):
        index = id // 0x1000000 * 0x1000000
        if self.handlers.get(id):
            return self.handlers[id]
        handler_mapping = {
            0x1000000: GPIOHandler,
            0x2000000: PWMHandler,
            0x3000000: TimerHandler,
            0x4000000: UARTHandler,
            0x5000000: I2CHandler,
            0x6000000: SPIHandler,
            0x7000000: ADCHandler,
            0x8000000: DACHandler,
        }
        handler_class = handler_mapping.get(index)
        if handler_class:
            self.handlers[id] = handler_class()
            return self.handlers[id]
        return None
