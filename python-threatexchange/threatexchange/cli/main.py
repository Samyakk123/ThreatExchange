# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

"""
A wrapper around multi-stage ThreatExchange operations.

Includes simple matching and writing back. Useful for quickly validating new
sources of ThreatExchange data. A possible template for a native
implementation in your own architecture.

This helper heavily relies on a config file to provide consistent behavior
between stages, and a state file to store hashes.
"""

import argparse
import logging
import inspect
import pathlib
import os
import sys
import typing as t

from threatexchange import meta

from threatexchange.fetcher.simple.static_sample import StaticSampleSignalExchangeAPI

from threatexchange.content_type import photo, video, text, url
from threatexchange.signal_type import (
    pdq,
    md5,
    raw_text,
    url as url_signal,
    url_md5,
    trend_query,
)
from threatexchange.cli.cli_config import CliState
from threatexchange.cli.cli_config import CLISettings
from threatexchange.cli import (
    command_base as base,
    fetch_cmd,
    label_cmd,
    dataset_cmd,
    hash_cmd,
    match_cmd,
)


def get_subcommands() -> t.List[t.Type[base.Command]]:
    return [
        fetch_cmd.FetchCommand,
        match_cmd.MatchCommand,
        label_cmd.LabelCommand,
        dataset_cmd.DatasetCommand,
        hash_cmd.HashCommand,
    ]


def get_argparse(settings: CLISettings) -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "--config",
        "-c",
        type=argparse.FileType("r"),
        help="a ThreatExchange collaboration config",
    )
    ap.add_argument(
        "--app-token",
        "-a",
        metavar="TOKEN",
        help="the App token for ThreatExchange",
    )
    ap.add_argument(
        "--fb-threatexchange-endpoint",
        "-E",
        # For facebook developers testing new APIs, allow pointing
        # to internal endpoints
        help=argparse.SUPPRESS,
    )
    subparsers = ap.add_subparsers(title="verbs", help="which action to do")
    for command in get_subcommands():
        command.add_command_to_subparser(settings, subparsers)

    return ap


def execute_command(settings: CLISettings, namespace) -> None:
    if not hasattr(namespace, "command_cls"):
        get_argparse().print_help()
        return
    command_cls = namespace.command_cls
    logging.debug("Setup complete, handing off to %s", command_cls.__name__)
    try:
        # Init everything
        command_argspec = inspect.getfullargspec(command_cls.__init__)
        arg_names = set(command_argspec[0])
        # Since we didn't import click, use hard-to-debug magic to init the command
        command = command_cls(
            **{k: v for k, v in namespace.__dict__.items() if k in arg_names}
        )
        command.execute(settings)
    except base.CommandError as ce:
        print(ce, file=sys.stderr)
        sys.exit(ce.returncode)
    except KeyboardInterrupt:
        # No stack for CTRL+C
        sys.exit(130)


def _get_settings():
    """
    Configure the behavior and functionality.
    """

    # Init API
    # api = ThreatExchangeAPI(
    #     get_app_token(namespace.app_token),
    #     endpoint_override=namespace.fb_threatexchange_endpoint,
    # )
    # Init state library (needs to be refactored)
    # descriptor.ThreatDescriptor.MY_APP_ID = api.api_token.partition("|")[0]
    # # Init collab config
    # cfg = init_config_file(namespace.config)
    # # "Init" dataset
    # dataset = Dataset(cfg, namespace.state_dir)

    signals = meta.SignalTypeMapping(
        [photo.PhotoContent, video.VideoContent, url.URLContent, text.TextContent],
        [
            pdq.PdqSignal,
            md5.VideoMD5Signal,
            raw_text.RawTextSignal,
            url_signal.URLSignal,
            url_md5.UrlMD5Signal,
            trend_query.TrendQuerySignal,
        ],
    )
    fetchers = meta.FetcherMapping(
        [
            StaticSampleSignalExchangeAPI(),
        ]
    )
    state = CliState(list(fetchers.fetchers_by_name.values()))

    return CLISettings(meta.FunctionalityMapping(signals, fetchers, state), state)


def _setup_logging():
    level = logging.DEBUG
    verbose = os.getenv("TX_VERBOSE", "0")
    if verbose == "0":
        level = logging.CRITICAL
    if verbose == "1":
        level = logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname).1s] %(message)s", level=level, force=True
    )


def main(args: t.Optional[t.Sequence[t.Text]] = None) -> None:
    _setup_logging()

    settings = _get_settings()
    ap = get_argparse(settings)
    namespace = ap.parse_args(args)
    execute_command(settings, namespace)


if __name__ == "__main__":
    main()
