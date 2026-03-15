import asyncio
import logging
from typing import List

logger = logging.getLogger("uvicorn")

class WorkerManager:
    """
    Класс для управления жизненным циклом фоновых воркеров.
    """
    def __init__(self, workers: List):
        """
        Инициализирует менеджер воркеров.

        :param workers: Список объектов воркеров для запуска.
        """
        self.workers = workers
        self._tasks = []

    async def start_all(self):
        """
        Запускает все зарегистрированные воркеры в виде асинхронных задач.
        """
        logger.info(f"Запуск {len(self.workers)} воркеров")
        for worker in self.workers:
            task = asyncio.create_task(worker.run())
            self._tasks.append(task)

    async def stop_all(self):
        """
        Останавливает все запущенные воркеры, отменяя их задачи.
        """
        logger.info("Остановка воркеров")
        for task in self._tasks:
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)
        logger.info("Все воркеры остановлены")
