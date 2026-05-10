from __future__ import annotations

import argparse
import json
import statistics
import sys
import threading
import time
import tracemalloc
from collections import defaultdict, deque
from pathlib import Path
from typing import TYPE_CHECKING

# tests/esp32_mqtt_stability_probe.py -> repo root is parent of tests/
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from config import BROKER_HOST as DEFAULT_BROKER_HOST
    from config import BROKER_PORT as DEFAULT_BROKER_PORT
except Exception:
    DEFAULT_BROKER_HOST = "localhost"
    DEFAULT_BROKER_PORT = 1883

from core.BaseFunctionBlock import BaseFunctionBlock
from core.BaseResource import BaseResource
from core.FBInterface import FBInterface
from core.FBs.E_CYCLE import E_CYCLE
from core.FBs.MQTT_PUBLISH import MQTT_PUBLISH
from core.FBs.MQTT_SUBSCRIBE import MQTT_SUBSCRIBE
from core.datatypes.IEC_STRING import IEC_STRING

if TYPE_CHECKING:
    from core.ECET import EventChainExecutionThread


class ProbeState:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.sent_by_angle: dict[int, deque[float]] = defaultdict(deque)
        self.sent_count = 0
        self.ack_count = 0
        self.matched_ack_count = 0
        self.unexpected_ack_count = 0
        self.invalid_payload_count = 0
        self.latencies_ms: list[float] = []
        self.invalid_payload_samples: list[str] = []
        self.unexpected_ack_samples: list[str] = []

    def record_send(self, angle: int, timestamp: float) -> None:
        with self._lock:
            self.sent_count += 1
            self.sent_by_angle[angle].append(timestamp)

    def record_ack(self, payload: str, timestamp: float) -> None:
        with self._lock:
            self.ack_count += 1
            if not payload.startswith("ACK:"):
                self.invalid_payload_count += 1
                self._append_sample(self.invalid_payload_samples, payload)
                return

            try:
                angle = int(payload[4:])
            except ValueError:
                self.invalid_payload_count += 1
                self._append_sample(self.invalid_payload_samples, payload)
                return

            pending = self.sent_by_angle.get(angle)
            if not pending:
                self.unexpected_ack_count += 1
                self._append_sample(self.unexpected_ack_samples, payload)
                return

            sent_at = pending.popleft()
            self.matched_ack_count += 1
            self.latencies_ms.append((timestamp - sent_at) * 1000.0)

    def snapshot(self) -> dict[str, object]:
        with self._lock:
            missing = sum(len(values) for values in self.sent_by_angle.values())
            latencies = list(self.latencies_ms)
            return {
                "published_count": self.sent_count,
                "ack_count": self.ack_count,
                "matched_ack_count": self.matched_ack_count,
                "missing_ack_count": missing,
                "unexpected_ack_count": self.unexpected_ack_count,
                "invalid_payload_count": self.invalid_payload_count,
                "invalid_payload_samples": list(self.invalid_payload_samples),
                "unexpected_ack_samples": list(self.unexpected_ack_samples),
                "latency_min_ms": round(min(latencies), 3) if latencies else None,
                "latency_mean_ms": round(statistics.mean(latencies), 3) if latencies else None,
                "latency_p95_ms": round(percentile(latencies, 0.95), 3) if latencies else None,
                "latency_max_ms": round(max(latencies), 3) if latencies else None,
            }

    @staticmethod
    def _append_sample(samples: list[str], value: str, limit: int = 5) -> None:
        if len(samples) < limit:
            samples.append(value)


class ProbeCounter360(BaseFunctionBlock):
    FBINTERFACE = FBInterface(
        ei_names=("REQ",),
        eo_names=("CNF",),
        do_names=("VALUE",),
        do_types=(IEC_STRING,),
    )

    _EI_REQ = 0
    _EO_CNF = 0
    _DO_VALUE = 0

    def __init__(self, instance_name: str, state: ProbeState, step: int) -> None:
        self._state_ref = state
        self._step = step
        self._angle = 0
        super().__init__(instance_name)

    def execute_event(self, ei_id: int, ecet: "EventChainExecutionThread") -> None:
        if ei_id == self._EI_REQ:
            angle = self._angle
            self._do_vars[self._DO_VALUE].value = str(angle)
            self._state_ref.record_send(angle, time.perf_counter())
            self._angle = (self._angle + self._step) % 360
            self.send_output_event(self._EO_CNF, ecet)

    def set_initial_values(self) -> None:
        self._angle = 0
        self._do_vars[self._DO_VALUE].value = "0"


class AckRecorder(BaseFunctionBlock):
    FBINTERFACE = FBInterface(
        ei_names=("REQ",),
        eo_names=("CNF",),
        di_names=("IN",),
        di_types=(IEC_STRING,),
    )

    _EI_REQ = 0
    _EO_CNF = 0
    _DI_IN = 0

    def __init__(self, instance_name: str, state: ProbeState) -> None:
        self._state_ref = state
        super().__init__(instance_name)

    def execute_event(self, ei_id: int, ecet: "EventChainExecutionThread") -> None:
        if ei_id == self._EI_REQ:
            self._state_ref.record_ack(str(self._di_vars[self._DI_IN].value), time.perf_counter())
            self.send_output_event(self._EO_CNF, ecet)

    def set_initial_values(self) -> None:
        self._di_vars[self._DI_IN].value = ""


def percentile(values: list[float], percent: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    index = min(round((len(ordered) - 1) * percent), len(ordered) - 1)
    return ordered[index]


def run_probe(
    *,
    broker_host: str,
    broker_port: int,
    duration_sec: float,
    period_ms: int,
    command_topic: str,
    status_topic: str,
    angle_step: int,
    init_grace_sec: float,
    final_grace_sec: float,
    min_ack_ratio: float,
    max_latency_ms: float,
) -> dict[str, object]:
    state = ProbeState()
    resource = BaseResource("esp32_probe_res")

    cycle = E_CYCLE("CYCLE")
    counter = ProbeCounter360("COUNTER", state, angle_step)
    publisher = MQTT_PUBLISH("PUB")
    subscriber = MQTT_SUBSCRIBE("SUB")
    recorder = AckRecorder("ACK_RECORDER", state)

    for fb in (cycle, counter, publisher, subscriber, recorder):
        resource.create_fb(fb)

    resource.set_data("CYCLE", "DT", period_ms)
    resource.set_data("PUB", "BROKER_HOST", broker_host)
    resource.set_data("PUB", "BROKER_PORT", broker_port)
    resource.set_data("PUB", "TOPIC", command_topic)
    resource.set_data("SUB", "BROKER_HOST", broker_host)
    resource.set_data("SUB", "BROKER_PORT", broker_port)
    resource.set_data("SUB", "TOPIC", status_topic)

    resource.connect_event("CYCLE", "EO", "COUNTER", "REQ")
    resource.connect_event("COUNTER", "CNF", "PUB", "SEND")
    resource.connect_event("SUB", "IND", "ACK_RECORDER", "REQ")
    resource.connect_data("COUNTER", "VALUE", "PUB", "VALUE")
    resource.connect_data("SUB", "VALUE", "ACK_RECORDER", "IN")

    tracemalloc.start()
    wall_start = time.perf_counter()
    cpu_start = time.process_time()

    resource.start()
    resource.trigger_event("SUB", "INIT")
    resource.trigger_event("PUB", "INIT")
    time.sleep(init_grace_sec)
    resource.trigger_event("CYCLE", "START")

    interrupted = False
    try:
        deadline = time.perf_counter() + duration_sec
        while time.perf_counter() < deadline:
            remaining = deadline - time.perf_counter()
            time.sleep(min(5.0, max(0.0, remaining)))
    except KeyboardInterrupt:
        interrupted = True
    finally:
        resource.trigger_event("CYCLE", "STOP")
        time.sleep(final_grace_sec)
        resource.trigger_event("PUB", "TERM")
        resource.trigger_event("SUB", "TERM")
        time.sleep(0.2)
        resource.stop()

    wall_end = time.perf_counter()
    cpu_end = time.process_time()
    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    snapshot = state.snapshot()
    published_count = int(snapshot["published_count"])
    matched_ack_count = int(snapshot["matched_ack_count"])
    ack_ratio = (matched_ack_count / published_count) if published_count else 0.0
    latency_max = snapshot["latency_max_ms"]
    latency_ok = latency_max is not None and float(latency_max) <= max_latency_ms
    passed = (
        not interrupted
        and published_count > 0
        and ack_ratio >= min_ack_ratio
        and latency_ok
        and int(snapshot["invalid_payload_count"]) == 0
    )

    result: dict[str, object] = {
        "passed": passed,
        "interrupted": interrupted,
        "duration_sec": round(wall_end - wall_start, 3),
        "test_duration_sec": duration_sec,
        "period_ms": period_ms,
        "broker_host": broker_host,
        "broker_port": broker_port,
        "command_topic": command_topic,
        "status_topic": status_topic,
        "angle_step": angle_step,
        "min_ack_ratio": min_ack_ratio,
        "actual_ack_ratio": round(ack_ratio, 6),
        "max_latency_ms_threshold": max_latency_ms,
        "cpu_time_sec": round(cpu_end - cpu_start, 3),
        "cpu_percent_estimate": round(((cpu_end - cpu_start) / (wall_end - wall_start)) * 100.0, 3),
        "tracemalloc_current_mb": round(current_mem / (1024 * 1024), 3),
        "tracemalloc_peak_mb": round(peak_mem / (1024 * 1024), 3),
    }
    result.update(snapshot)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Run an end-to-end BOLT MQTT stability probe with a real ESP32 client. "
            "ESP32 must run BOLT_mp and reply ENGINE_STATUS=ACK:<angle>."
        )
    )
    parser.add_argument("--broker-host", default=DEFAULT_BROKER_HOST)
    parser.add_argument("--broker-port", type=int, default=DEFAULT_BROKER_PORT)
    parser.add_argument("--duration-sec", type=float, default=600.0)
    parser.add_argument("--period-ms", type=int, default=500)
    parser.add_argument("--command-topic", default="ENGINE_DEGREES")
    parser.add_argument("--status-topic", default="ENGINE_STATUS")
    parser.add_argument("--angle-step", type=int, default=10)
    parser.add_argument("--init-grace-sec", type=float, default=2.0)
    parser.add_argument("--final-grace-sec", type=float, default=5.0)
    parser.add_argument("--min-ack-ratio", type=float, default=0.95)
    parser.add_argument("--max-latency-ms", type=float, default=1000.0)
    parser.add_argument("--no-fail", action="store_true", help="Always exit with code 0 after printing JSON.")
    parser.add_argument("--output-json", type=Path, default=None)
    args = parser.parse_args()

    result = run_probe(
        broker_host=args.broker_host,
        broker_port=args.broker_port,
        duration_sec=args.duration_sec,
        period_ms=args.period_ms,
        command_topic=args.command_topic,
        status_topic=args.status_topic,
        angle_step=args.angle_step,
        init_grace_sec=args.init_grace_sec,
        final_grace_sec=args.final_grace_sec,
        min_ack_ratio=args.min_ack_ratio,
        max_latency_ms=args.max_latency_ms,
    )

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)
    if args.output_json is not None:
        args.output_json.write_text(output + "\n", encoding="utf-8")

    if not result["passed"] and not args.no_fail:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
