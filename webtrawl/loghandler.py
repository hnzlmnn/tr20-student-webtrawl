import os
from datetime import datetime
from logging import handlers


class TimestampedRotatingFileHandler(handlers.RotatingFileHandler):
    def doRollover(self):
        if self.stream:
            self.stream.close()
            self.stream = None

        now = datetime.now()
        dfn = self.rotation_filename("{}_{}-{:02d}-{:02d}_{:02d}:{:02d}:{:02d}.{:02d}".format(
            self.baseFilename,
            now.year,
            now.month,
            now.day,
            now.hour,
            now.minute,
            now.second,
            now.microsecond,
        ))
        if os.path.exists(dfn):
            os.remove(dfn)
        self.rotate(self.baseFilename, dfn)
        if not self.delay:
            self.stream = self._open()
