import asyncio
import logging
import click
import sys
import os
from contextlib import contextmanager, suppress, redirect_stderr, redirect_stdout
from async_generator import asynccontextmanager

from .utils import remove_ansi_escape_sequences, capture_subprocess_output


class OutputLogger(object):
    def __init__(self, file):
        self.file = file
        self.stdout = sys.stdout
        self.stderr = sys.stderr

        self.outs = {}
        self._max_name_length = None

    def out(self, name, stream=None, color=None):
        if stream in (None, sys.stderr):
            stream = self.stderr
        elif stream is sys.stdout:
            stream = self.stdout

        out = Out(self, name, file=self.file, stream=stream, color=color)
        self.outs[name] = out
        self._max_name_length = None

        return out

    @property
    def max_name_length(self):
        if self._max_name_length is None:
            name_lengths = [len(name) for name in self.outs.keys()]
            self._max_name_length = max(name_lengths, default=0)

        return self._max_name_length

    def write_prefix(self, out):
        padding = max(self.max_name_length, 6)
        padded_name = out.name.ljust(padding)

        click.secho(f"{padded_name} | ", fg=out.color, nl=False, file=out)


class LineWriter(object):
    def __init__(self, out):
        self.__out = out

    def __getattr__(self, name):
        return getattr(self.__out, name)

    def write(self, line):
        self.__out.writeline(line)


class FileDescriptorWriter(object):
    def __init__(self, out, fd):
        self.__out = out
        self.__writer = os.fdopen(fd, "w")

    def __getattr__(self, name):
        return getattr(self.__writer, name)

    def isatty(self):
        return self.__out.isatty()


class Out(object):
    """
    Simple Out class to log anything written in a stream to a file
     and then also write it to the stream.
    """

    def __init__(self, output_logger, name, file, stream, color="white"):
        self.output_logger = output_logger
        self.name = name
        self.color = color

        self.file = file
        self.stream = stream


    @contextmanager
    def line_writer(self):
        yield LineWriter(self)

    @contextmanager
    def redirect_logging(self, format=None, ignore_errors=()):
        logger = logging.getLogger()
        original_log_handlers = logger.handlers

        line_writer = LineWriter(self)
        handler = logging.StreamHandler(line_writer)

        if not format:
            if logger.getEffectiveLevel() == logging.DEBUG:
                format = "%(levelname)s %(message)s"
            else:
                format = "%(message)s"

        formatter = logging.Formatter(fmt=format)
        handler.setFormatter(formatter)

        logger.handlers = [handler]

        try:
            yield
        except (KeyboardInterrupt, asyncio.CancelledError, *ignore_errors):
            raise
        except Exception as err:
            logger.error(str(err), exc_info=True)
            raise
        finally:
            logger.handlers = original_log_handlers

    @asynccontextmanager
    async def writer(self):
        read_fd, write_fd = os.pipe()

        reader = asyncio.ensure_future(self.read_from_fd(read_fd))
        writer = FileDescriptorWriter(self, write_fd)

        try:
            yield writer
        finally:
            writer.close()

            with suppress(asyncio.CancelledError):
                await reader

    @asynccontextmanager
    async def redirect_stdout(self):
        async with self.writer() as stdout:
            with redirect_stdout(stdout):
                yield

    @asynccontextmanager
    async def redirect_stderr(self):
        async with self.writer() as stderr:
            with redirect_stderr(stderr):
                yield

    def writeline(self, line):
        self.output_logger.write_prefix(self)
        self.write(line)
        self.flush()

    def write(self, data):
        self.stream.write(data)
        self.file.write(remove_ansi_escape_sequences(data))
        # always flush the file to keep it up to date with the stream
        self.file.flush()

    def flush(self):
        self.stream.flush()
        self.file.flush()

    def isatty(self):
        # Explicitly claim we're connected to a TTY to stop Click
        # from stripping ANSI codes
        return self.stream.isatty()

    async def read_from_fd(self, read_fd):
        reader = asyncio.StreamReader()
        read_protocol = asyncio.StreamReaderProtocol(reader)

        loop = asyncio.get_event_loop()
        read_transport, _ = await loop.connect_read_pipe(
            lambda: read_protocol, os.fdopen(read_fd)
        )

        await capture_subprocess_output(reader, self)
