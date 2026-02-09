import asyncio
from core.BaseFb import BaseFB

class E_CYCLE(BaseFB):
    def __init__(self, name: str):
        super().__init__(name)
        self._cycle_task: asyncio.Task | None = None

    async def execute(self, event: str):
        if event == "START":
            if self._cycle_task and not self._cycle_task.done():
                self._cycle_task.cancel()
                try:
                    await self._cycle_task
                except asyncio.CancelledError:
                    pass
            
            dt = self._inputs.get("DT", 1000)
            dt_seconds = dt / 1000.0
            
            self._cycle_task = asyncio.create_task(self._cycle(dt_seconds))
            return {}, []
            
        elif event == "STOP":
            if self._cycle_task and not self._cycle_task.done():
                self._cycle_task.cancel()
                try:
                    await self._cycle_task
                except asyncio.CancelledError:
                    pass
            self._cycle_task = None
            return {}, []
        
        return {}, []

    async def _cycle(self, dt_seconds: float):
        try:
            while True:
                await asyncio.sleep(dt_seconds)
                await self._emit_event("EO")
        except asyncio.CancelledError:
            pass
