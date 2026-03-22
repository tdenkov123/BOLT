import signal
import threading

from core.BaseDevice import BaseDevice
from core.BaseResource import BaseResource
from core.FunctionBlockLoader import FunctionBlockLoader
from core.BaseFunctionBlock import BaseFunctionBlock
from core.FBs.PRINT_CONSOLE import PRINT_CONSOLE
from core.FBInterface import FBInterface
from core.datatypes.IEC_STRING import IEC_STRING
from core.datatypes.IEC_INT import IEC_DINT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread

class COUNTER_360(BaseFunctionBlock):
    FBINTERFACE = FBInterface(
        ei_names=("REQ",),
        eo_names=("CNF",),
        do_names=("VALUE",),
        do_types=(IEC_STRING,),
    )

    _EI_REQ = 0
    _EO_CNF = 0
    _DO_VALUE = 0

    def __init__(self, instance_name: str) -> None:
        self._angle = 0
        super().__init__(instance_name)

    def execute_event(self, ei_id: int, ecet: "EventChainExecutionThread") -> None:
        if ei_id == self._EI_REQ:
            self._do_vars[self._DO_VALUE].value = str(self._angle)
            self._angle = (self._angle + 10) % 360
            self.send_output_event(self._EO_CNF, ecet)

    def set_initial_values(self) -> None:
        self._do_vars[self._DO_VALUE].value = "0"


class PRINT_TX(PRINT_CONSOLE):
    def execute_event(self, ei_id: int, ecet: "EventChainExecutionThread") -> None:
        if ei_id == self._EI_REQ:
            print("[TX] ENGINE_DEGREES =", self._di_vars[self._DI_IN].value)
            self.send_output_event(self._EO_CNF, ecet)


class PRINT_RX(PRINT_CONSOLE):
    def execute_event(self, ei_id: int, ecet: "EventChainExecutionThread") -> None:
        if ei_id == self._EI_REQ:
            print("[RX] ENGINE_STATUS  =", self._di_vars[self._DI_IN].value)
            self.send_output_event(self._EO_CNF, ecet)


from config import BROKER_HOST, BROKER_PORT


def main() -> None:
    loader = FunctionBlockLoader()
    classes = loader.loadFBList([
        "core.FBs.START",
        "core.FBs.E_CYCLE",
        "core.FBs.E_DELAY",
        "core.FBs.PRINT_CONSOLE",
        "core.FBs.MQTT_PUBLISH",
        "core.FBs.MQTT_SUBSCRIBE",
    ])

    dev = BaseDevice("dev1")
    res = BaseResource("res1")
    dev.add_resource(res)

    res.create_fb(classes["START"]("START"))
    res.create_fb(classes["E_CYCLE"]("CYCLE"))
    res.create_fb(COUNTER_360("COUNTER"))
    res.create_fb(classes["MQTT_PUBLISH"]("PUB"))
    res.create_fb(classes["MQTT_SUBSCRIBE"]("SUB"))
    res.create_fb(PRINT_RX("PRINT"))
    res.create_fb(PRINT_TX("PRINT_TX"))
    res.create_fb(classes["PRINT_CONSOLE"]("PRINT_CONN"))

    res.set_data("CYCLE", "DT", 500)
    res.set_data("PUB", "BROKER_HOST", BROKER_HOST)
    res.set_data("PUB", "BROKER_PORT", BROKER_PORT)
    res.set_data("PUB", "TOPIC", "ENGINE_DEGREES")
    res.set_data("SUB", "BROKER_HOST", BROKER_HOST)
    res.set_data("SUB", "BROKER_PORT", BROKER_PORT)
    res.set_data("SUB", "TOPIC", "ENGINE_STATUS")
    res.set_data("PRINT_CONN", "IN", "[BOLT] MQTT broker connected")

    res.connect_event("START", "START", "PUB",   "INIT")
    res.connect_event("START", "START", "SUB",   "INIT")
    res.connect_event("START", "START", "CYCLE", "START")
    res.connect_event("PUB", "INITO", "PRINT_CONN", "REQ")
    res.connect_event("CYCLE",   "EO",    "COUNTER",  "REQ")
    res.connect_event("COUNTER", "CNF",   "PRINT_TX", "REQ")
    res.connect_event("COUNTER", "CNF",   "PUB",      "SEND")
    res.connect_event("SUB", "IND", "PRINT", "REQ")

    res.connect_data("COUNTER", "VALUE", "PUB",   "VALUE")
    res.connect_data("SUB", "VALUE", "PRINT", "IN")
    res.connect_data("COUNTER", "VALUE", "PRINT_TX", "IN")

    print(f"[BOLT] Connecting to broker at {BROKER_HOST}:{BROKER_PORT} ...")
    dev.start()
    dev.trigger_event("res1", "START", event="START")

    stop = threading.Event()
    signal.signal(signal.SIGINT, lambda s, f: stop.set())
    try:
        stop.wait()
    except KeyboardInterrupt:
        pass
    finally:
        dev.stop()
        print("[BOLT] Stopped.")


if __name__ == "__main__":
    main()
