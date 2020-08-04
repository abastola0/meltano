import pytest
import tempfile
import io
import logging
import sys
from pathlib import Path

from meltano.core.logging.output_logger import OutputLogger


class TestOutputLogger:
    @pytest.fixture
    def log(self, tmp_path):
        return tempfile.TemporaryFile(mode="w+", dir=tmp_path)
        # return io.StringIO()

    @pytest.fixture
    def subject(self, log):
        return OutputLogger(log)

    @pytest.mark.asyncio
    async def test_out(self, log, subject):
        stdout_out = subject.out("stdout")
        stderr_out = subject.out("stderr")
        logging_out = subject.out("logging")
        writer_out = subject.out("writer")
        line_writer_out = subject.out("lwriter")
        basic_out = subject.out("basic")

        async with stdout_out.redirect_stdout():
            sys.stdout.write("STD")
            sys.stdout.write("OUT\n")
            print("STDOUT 2")

        async with stderr_out.redirect_stderr():
            sys.stderr.write("STD")
            sys.stderr.write("ERR\n")
            print("STDERR 2", file=sys.stderr)

        with logging_out.redirect_logging():
            logging.info("info")
            logging.warning("warning")
            logging.error("error")

        async with writer_out.writer() as writer:
            writer.write("WRI")
            writer.write("TER\n")
            writer.write("WRITER 2\n")

        with line_writer_out.line_writer() as line_writer:
            line_writer.write("LINE\n")
            line_writer.write("LINE 2\n")

        basic_out.writeline("LINE\n")
        basic_out.writeline("LINE 2\n")

        # read from the beginning
        log.seek(0)
        log_content = log.read()

        assert "stdout  | STDOUT" in log_content
        assert "stdout  | STDOUT 2" in log_content
        assert "stderr  | STDERR" in log_content
        assert "stderr  | STDERR 2" in log_content
        assert "logging | INFO info" in log_content
        assert "logging | WARNING warning" in log_content
        assert "logging | ERROR error" in log_content
        assert "writer  | WRITER" in log_content
        assert "writer  | WRITER 2" in log_content
        assert "lwriter | LINE" in log_content
        assert "lwriter | LINE 2" in log_content
        assert "basic   | LINE" in log_content
        assert "basic   | LINE 2" in log_content

    def test_logging_exception(self, log, subject):
        logging_out = subject.out("logging")

        # it raises logs unhandled exceptions
        exception = Exception("exception")

        with pytest.raises(Exception) as exc:
            with logging_out.redirect_logging():
                raise exception

        # make sure it let the exception through
        assert exc.value is exception

        # read from the beginning
        log.seek(0)
        log_content = log.read()

        # make sure the exception is logged
        assert "logging | ERROR exception" in log_content
