# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

"""
A way to connect all the key interfaces of the library.

Since matching may need to look up context from the original fetching,
this is all the parts needed to get you there.

You don't need to do it this way, but it does make it clear which
fetching, matching, and other capabilities you are supporting.
"""

import typing as t
from dataclasses import dataclass

from threatexchange.content_type.content_base import ContentType
from threatexchange.signal_type.signal_base import SignalType
from threatexchange.fetcher.fetch_api import SignalExchangeAPI
from threatexchange.fetcher.fetch_state import FetchedStateBase
from threatexchange.fetcher.collab_config import CollaborationConfigStoreBase


class SignalTypeMapping:
    def __init__(
        self,
        content_types: t.List[t.Type[ContentType]],
        signal_types: t.List[t.Type[SignalType]],
    ):
        _validate_content_and_signal(content_types, signal_types)

        self.content_by_name = {c.get_name(): c for c in content_types}
        self.signal_type_by_name = {s.get_name(): s for s in signal_types}

    def get_fetcher_classes(self):
        return [f[0] for f in self.fetcher_data_by_name.values()]

    def get_supported_signal_types_for_content(
        self, content: t.Type[ContentType]
    ) -> t.List[t.Type[SignalType]]:
        return [
            s
            for s in content.get_signal_types()
            if s.get_name() in self.signal_type_by_name
        ]


class FetcherSyncer(t.NamedTuple):
    api: SignalExchangeAPI
    store: FetchedStateBase


class FetcherMapping:
    def __init__(self, fetchers: t.List[FetcherSyncer]) -> None:
        _validate_signal_apis(f.api for f in fetchers)
        self.fetchers_by_name = {f.api.get_name(): f for f in fetchers}


@dataclass
class FunctionalityMapping:
    """
    All of key fetch, hash, match interfaces combined.

    Since matching may need to look up context from the original fetching,
    this container provides all the interfaces needed to get you there.
    """

    signal_and_content: SignalTypeMapping
    fetcher: FetcherMapping
    collabs: CollaborationConfigStoreBase


def _validate_signal_apis(self, apis: t.Iterable[SignalExchangeAPI]):
    names = set()
    for a in apis:
        name = a.get_name()
        assert (
            name not in names
        ), f"Duplicate name in {SignalExchangeAPI.__name__}s: '{name}'"
        names.add(name)


def _validate_content_types(content_types: t.List[t.Type[ContentType]]) -> None:
    names = set()
    for c in content_types:
        name = c.get_name()
        assert name not in names, f"Duplicate name in {ContentType.__name__}s: '{name}'"
        names.add(name)


def _validate_signal_types(self, signal_types: t.List[t.Type[SignalType]]):
    names = set()
    for s in signal_types:
        name = s.get_name()
        assert name not in names, f"Duplicate name in {SignalType.__name__}s: '{name}'"
        names.add(name)


def _validate_content_and_signal(
    self,
    content_types: t.List[t.Type[ContentType]],
    signal_types: t.List[t.Type[SignalType]],
) -> None:
    _validate_content_types(content_types)
    _validate_signal_types(signal_types)
    supported_st = set(signal_types)
    for content_type in content_types:
        supported = any(s in supported_st for s in content_type.get_signal_types())
        assert supported, f"No signal types for content type: {content_type.get_name()}"

    pass
