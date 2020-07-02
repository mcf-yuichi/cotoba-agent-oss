"""
Copyright (c) 2020 COTOBA DESIGN, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
"""
Copyright (c) 2016-2019 Keith Sterling http://www.keithsterling.com

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import sys
import logging
import traceback
import json
import datetime


class YLoggerSnapshot(object):

    def __init__(self, criticals=0, fatals=0, errors=0, exceptions=0, warnings=0, infos=0, debugs=0):
        self._criticals = criticals
        self._fatals = fatals
        self._errors = errors
        self._exceptions = exceptions
        self._warnings = warnings
        self._infos = infos
        self._debugs = debugs

    def __str__(self):
        return "Critical(%d) Fatal(%d) Error(%d) Exception(%d) Warning(%d) Info(%d), Debug(%d)" % (
            self._criticals, self._fatals, self._errors, self._exceptions, self._warnings, self._infos, self._debugs
        )


class YLogger(object):

    CRITICALS = 0
    FATALS = 0
    ERRORS = 0
    EXCEPTIONS = 0
    WARNINGS = 0
    INFOS = 0
    DEBUGS = 0
    IS_STDOUT = False
    IS_STDERR = False
    PREFIX = "Yadlan"
    IS_TRACEBACK = True
    DEFAULT_LEVEL = None

    @staticmethod
    def snapshot():
        return YLoggerSnapshot(YLogger.CRITICALS,
                               YLogger.FATALS,
                               YLogger.ERRORS,
                               YLogger.EXCEPTIONS,
                               YLogger.WARNINGS,
                               YLogger.INFOS,
                               YLogger.DEBUGS)

    @staticmethod
    def reset_snapshot():
        YLogger.CRITICALS = 0
        YLogger.FATALS = 0
        YLogger.ERRORS = 0
        YLogger.EXCEPTIONS = 0
        YLogger.WARNINGS = 0
        YLogger.INFOS = 0
        YLogger.DEBUGS = 0

    @staticmethod
    def format_message(caller, message):
        if caller is not None:
            if hasattr(caller, "ylogger_type"):
                log_type = caller.ylogger_type()
                if log_type == 'client':
                    return "[%s] - %s" % (caller.id, message)
                elif log_type == 'bot':
                    return "[%s] [%s] - %s" % (caller.client.id if caller.client is not None else "",
                                               caller.id, message)
                elif log_type == 'brain':
                    clientid = ""
                    botid = ""
                    if caller.bot is not None:
                        if caller.bot.client is not None:
                            clientid = caller.bot.client.id
                        botid = caller.bot.id
                    return "[%s] [%s] [%s] - %s" % (clientid, botid, caller.id, message)
                elif log_type == 'context':
                    return "[%s] [%s] [%s] [%s] - %s" % (caller.client.id if caller.client is not None else "",
                                                         caller.bot.id if caller.bot is not None else "",
                                                         caller.brain.id if caller.brain is not None else "",
                                                         caller.userid, message)
        return message

    @staticmethod
    def set_default_level():
        YLogger.DEFAULT_LEVEL = 'none'
        level = logging.getLogger().getEffectiveLevel()
        if level == logging.CRITICAL or \
           level == logging.FATAL or \
           level == logging.ERROR:
            YLogger.DEFAULT_LEVEL = 'error'
        elif level == logging.WARNING:
            YLogger.DEFAULT_LEVEL = 'warning'
        elif level == logging.INFO:
            YLogger.DEFAULT_LEVEL = 'info'
        elif level == logging.DEBUG:
            YLogger.DEFAULT_LEVEL = 'debug'

        logging.getLogger().setLevel(level=logging.DEBUG)

    @staticmethod
    def check_loglevel(caller, level):
        if YLogger.DEFAULT_LEVEL is None:
            return logging.getLogger().isEnabledFor(level)

        out_level = YLogger.DEFAULT_LEVEL
        if caller is not None:
            if hasattr(caller, "get_loglevel"):
                client_loglevel = caller.get_loglevel()
                if client_loglevel is not None:
                    out_level = client_loglevel

        if level == logging.CRITICAL or \
           level == logging.FATAL or \
           level == logging.ERROR:
            if out_level in ['error', 'warning', 'info', 'debug']:
                return True
        elif level == logging.WARNING:
            if out_level in ['warning', 'info', 'debug']:
                return True
        elif level == logging.INFO:
            if out_level in ['info', 'debug']:
                return True
        elif level == logging.DEBUG:
            if out_level == 'debug':
                return True
        return False

    @staticmethod
    def critical(caller, message, *args, **kwargs):
        YLogger.CRITICALS += 1
        if YLogger.check_loglevel(caller, logging.CRITICAL):
            logging.critical(YLogger.format_message(caller, message), *args, **kwargs)
            YLogger.yadlan_stderr(caller, "critical", message, *args, **kwargs)

    @staticmethod
    def fatal(caller, message, *args, **kwargs):
        YLogger.FATALS += 1
        if YLogger.check_loglevel(caller, logging.FATAL):
            logging.fatal(YLogger.format_message(caller, message), *args, **kwargs)
            YLogger.yadlan_stderr(caller, "fatal", message, *args, **kwargs)

    @staticmethod
    def error(caller, message, *args, **kwargs):
        YLogger.ERRORS += 1
        if YLogger.check_loglevel(caller, logging.ERROR):
            logging.error(YLogger.format_message(caller, message), *args, **kwargs)
            YLogger.yadlan_stderr(caller, "error", message, *args, **kwargs)

    @staticmethod
    def exception(caller, message, exception, *args, **kwargs):
        YLogger.EXCEPTIONS += 1
        if YLogger.check_loglevel(caller, logging.ERROR):
            excep_msg = "%s [%s]" % (message, str(exception))
            logging.error(YLogger.format_message(caller, excep_msg), *args, **kwargs)
            if YLogger.IS_TRACEBACK is True and exception is not None:
                tb_lines = [line.rstrip('\n') for line in
                            traceback.format_exception(exception.__class__, exception, exception.__traceback__)]
                for line in tb_lines:
                    logging.error(YLogger.format_message(caller, line))
                    YLogger.yadlan_stderr(caller, "exception", message, *args, **kwargs)

    @staticmethod
    def warning(caller, message, *args, **kwargs):
        YLogger.WARNINGS += 1
        if YLogger.check_loglevel(caller, logging.WARNING):
            logging.warning(YLogger.format_message(caller, message), *args, **kwargs)
            YLogger.yadlan_stdout(caller, "warning", message, *args, **kwargs)

    @staticmethod
    def info(caller, message, *args, **kwargs):
        YLogger.INFOS += 1
        if YLogger.check_loglevel(caller, logging.INFO):
            logging.info(YLogger.format_message(caller, message), *args, **kwargs)
            YLogger.yadlan_stdout(caller, "info", message, *args, **kwargs)

    @staticmethod
    def debug(caller, message, *args, **kwargs):
        YLogger.DEBUGS += 1
        if YLogger.check_loglevel(caller, logging.DEBUG):
            logging.debug(YLogger.format_message(caller, message), *args, **kwargs)
            YLogger.yadlan_stdout(caller, "debug", message, *args, **kwargs)

    @staticmethod
    def set_stdout(status):
        if status != "True":
            YLogger.IS_STDOUT = False
        else:
            YLogger.IS_STDOUT = True

    @staticmethod
    def set_stderr(status):
        if status != "True":
            YLogger.IS_STDERR = False
        else:
            YLogger.IS_STDERR = True

    @staticmethod
    def set_prefix(prefix):
        YLogger.PREFIX = prefix

    @staticmethod
    def set_traceback(setting: bool):
        YLogger.IS_TRACEBACK = setting

    @staticmethod
    def format_yadlan_message(prefix, level, caller, message):
        botid = ""
        brainid = ""
        userid = ""
        try:
            botid = caller.bot.id
        except Exception:
            pass
        try:
            brainid = caller.brain.id
        except Exception:
            pass
        try:
            userid = caller.userid
        except Exception:
            pass

        messageDict = message
        try:
            messageDict = json.loads(message, encoding="utf-8")
        except Exception:
            pass

        dt_now = datetime.datetime.now()

        dict = {"time": str(dt_now), "status": level, "bot_id": prefix, "botid": botid, "brainid": brainid, "userid": userid, "message": messageDict}
        return json.dumps(dict, ensure_ascii=False)

    @staticmethod
    def yadlan_stdout(caller, level, message, *args, **kwargs):
        if YLogger.IS_STDOUT:
            if len(args) == 0:
                sys.stdout.write(YLogger.format_yadlan_message(YLogger.PREFIX, level, caller, message) + "\n")
            else:
                sys.stdout.write(YLogger.format_yadlan_message(YLogger.PREFIX, level, caller, message) % args + "\n")
            sys.stdout.flush()

    @staticmethod
    def yadlan_stderr(caller, level, message, *args, **kwargs):
        if YLogger.IS_STDERR:
            sys.stderr.write(YLogger.format_yadlan_message(YLogger.PREFIX, level, caller, message) % args + "\n")
            sys.stderr.flush()
