#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import psutil
import logging
import time
import shutil
import platform
import signal
import subprocess

from ..common.settings import HFFS_EXEC_NAME


def daemon_start(args):
    process_running = list(filter(
        lambda p: p.name().startswith(HFFS_EXEC_NAME) and "daemon" in p.cmdline() and "start" in p.cmdline(),
        psutil.process_iter(attrs=["pid", "name", "cmdline"])))

    if len(process_running) > 1:
        raise LookupError("Service already start!")

    exec_path = shutil.which(HFFS_EXEC_NAME)

    if not exec_path:
        raise FileNotFoundError(HFFS_EXEC_NAME)

    # deal zombie process
    if platform.system() in ["Linux"]:
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    cmdline_daemon_false = "--daemon=false"

    _ = subprocess.Popen([exec_path, "daemon", "start", "--port={}".format(args.port), cmdline_daemon_false],
                         stdin=subprocess.DEVNULL,
                         stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL)

    time.sleep(1)

    if platform.system() in ["Darwin"]:
        process_running = list(
            filter(
                lambda p:
                p.name().endswith("Python") and
                any(HFFS_EXEC_NAME in word for word in p.cmdline()) and
                "daemon" in p.cmdline() and
                "start" in p.cmdline() and
                cmdline_daemon_false in p.cmdline(),
                psutil.process_iter(attrs=["pid", "name", "cmdline"])))

        if len(process_running) != 1:
            raise ProcessLookupError("Service not is one，check service!")
    else:
        process_running = list(
            filter(
                lambda p:
                p.name().startswith(HFFS_EXEC_NAME) and
                "daemon" in p.cmdline() and
                "start" in p.cmdline() and
                cmdline_daemon_false in p.cmdline(),
                psutil.process_iter(attrs=["pid", "name", "cmdline"])))

        if len(process_running) != 1:
            raise ProcessLookupError("Service not is one，check service!")

    print("Daemon process started successfully")


def daemon_stop_on_mac():
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        if (proc.name().endswith("Python") and any(HFFS_EXEC_NAME in word for word in proc.cmdline()) and "daemon" in
                proc.cmdline() and "start" in proc.cmdline()):
            logging.info("Try to stop service {} ...".format(proc.name()))
            proc.terminate()
            wait_process_exit_time = 3
            time.sleep(wait_process_exit_time)

            if proc.is_running():
                proc.kill()

            if proc.is_running():
                logging.warning("Process killed but still running! service: {}, pid: {}"
                                .format(proc.name(), proc.pid))
            else:
                logging.info("Service stopped!")


def daemon_stop_common():
    for proc in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
        if proc.name().startswith(HFFS_EXEC_NAME) and "daemon" in proc.cmdline() and "start" in proc.cmdline():
            logging.info("Try to stop service {} ...".format(proc.name()))
            proc.terminate()
            wait_process_exit_time = 3
            time.sleep(wait_process_exit_time)

            if proc.is_running():
                proc.kill()

            if proc.is_running():
                logging.warning("Process killed but still running! service: {}, pid: {}"
                                .format(proc.name(), proc.pid))
            else:
                logging.info("Service stopped!")


def daemon_stop():
    if platform.system() in ["Darwin"]:
        daemon_stop_on_mac()
    else:
        daemon_stop_common()
