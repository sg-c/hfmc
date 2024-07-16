"""Utils for args parsing and usage."""

from __future__ import annotations

import argparse
import logging
from argparse import Namespace

from hffs.common.context import HffsContext


def is_detached_daemon(args: Namespace) -> bool:
    """Check if HFFS is running as a detached daemon."""
    return args.command == "daemon" and args.daemon_command == "start" and args.detach


def get_logging_level(args: Namespace) -> int:
    """Get logging level from args."""
    if args.verbose:
        return logging.DEBUG
    return logging.INFO


# pylint: disable=too-many-locals,too-many-statements
def arg_parser() -> Namespace:  # noqa: PLR0915
    """Parse args."""
    df_port = HffsContext.get_port()

    parser = argparse.ArgumentParser(prog="hffs")
    parser.add_argument("-v", "--verbose", action="store_true")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # hffs daemon ...
    daemon_parser = subparsers.add_parser("daemon")
    daemon_subparsers = daemon_parser.add_subparsers(
        dest="daemon_command",
        required=True,
    )
    # hffs daemon start ...
    daemon_start_parser = daemon_subparsers.add_parser("start")
    daemon_start_parser.add_argument("-d", "--detach", action="store_true")
    # hffs daemon stop
    daemon_subparsers.add_parser("stop")
    # hffs daemon status
    daemon_subparsers.add_parser("status")

    # hffs peer ...
    peer_parser = subparsers.add_parser("peer")
    peer_subparsers = peer_parser.add_subparsers(
        dest="peer_command",
        required=True,
    )
    # hffs peer add ...
    peer_add_parser = peer_subparsers.add_parser("add")
    peer_add_parser.add_argument("ip")
    peer_add_parser.add_argument("-p", "--port", type=int, default=df_port)
    # hffs peer rm ...
    peer_rm_parser = peer_subparsers.add_parser("rm")
    peer_rm_parser.add_argument("ip")
    peer_rm_parser.add_argument("-p", "--port", type=int, default=df_port)
    # hffs peer ls ...
    peer_subparsers.add_parser("ls")

    # hffs model ...
    model_parser = subparsers.add_parser("model")
    model_subparsers = model_parser.add_subparsers(
        dest="model_command",
        required=True,
    )
    # hffs model ls ...
    model_ls_parser = model_subparsers.add_parser("ls")
    model_ls_parser.add_argument("-r", "--repo")
    # hffs model add ...
    model_add_parser = model_subparsers.add_parser("add")
    model_add_parser.add_argument("-r", "--repo", required=True)
    model_add_parser.add_argument("-f", "--file")
    model_add_parser.add_argument("-v", "--revision", default="main")
    # hffs model rm ...
    model_rm_parser = model_subparsers.add_parser("rm")
    model_rm_parser.add_argument("-r", "--repo", required=True)
    model_rm_parser.add_argument("-f", "--file")
    model_rm_parser.add_argument("-v", "--revision")
    # hffs model search ...
    model_search_parser = model_subparsers.add_parser("search")
    model_search_parser.add_argument("-r", "--repo", required=True)
    model_search_parser.add_argument("-f", "--file")
    model_search_parser.add_argument("-v", "--revision", default="main")

    # hffs conf ...
    conf_parser = subparsers.add_parser("conf")
    conf_subparsers = conf_parser.add_subparsers(
        dest="conf_command",
        required=True,
    )
    # hffs conf cache ...
    conf_cache_parser = conf_subparsers.add_parser("cache")
    conf_cache_subparsers = conf_cache_parser.add_subparsers(
        dest="conf_cache_command",
        required=True,
    )
    conf_cache_set_parser = conf_cache_subparsers.add_parser("set")
    conf_cache_set_parser.add_argument("path")
    conf_cache_subparsers.add_parser("get")
    conf_cache_subparsers.add_parser("reset")
    # hffs conf port ...
    conf_port_parser = conf_subparsers.add_parser("port")
    conf_port_subparsers = conf_port_parser.add_subparsers(
        dest="conf_port_command",
        required=True,
    )
    conf_port_set_subparser = conf_port_subparsers.add_parser("set")
    conf_port_set_subparser.add_argument("port", type=int)
    conf_port_subparsers.add_parser("get")
    conf_port_subparsers.add_parser("reset")
    # hffs conf show
    conf_subparsers.add_parser("show")

    # hffs auth ...
    auth_parser = subparsers.add_parser("auth")
    auth_subparsers = auth_parser.add_subparsers(
        dest="auth_command",
        required=True,
    )
    # hffs auth login
    auth_subparsers.add_parser("login")
    # hffs auth logout
    auth_subparsers.add_parser("logout")

    # hffs uninstall
    subparsers.add_parser("uninstall")

    return parser.parse_args()
