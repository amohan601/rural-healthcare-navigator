import json
import logging

from src.backend.logging.context import thread_id_var, agent_var


class JsonFormatter(logging.Formatter):

    def format(self, record):

        log = {
            "timestamp": self.formatTime(record),
            "level": record.levelname,
            "thread_id": thread_id_var.get(),
            "agent": agent_var.get(),
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        return json.dumps(log)