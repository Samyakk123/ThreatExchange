#!/usr/bin/env python
# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

"""
Settings used to inform a fetcher what to fetch
"""

from dataclasses import dataclass
import typing as t

from threatexchange.collab_config import CollaborationConfig
from threatexchange.fetcher.fetch_api import SignalExchangeAPI


@dataclass
class CollaborationConfigBase:
    """
    Settings used to inform a fetcher what to fetch.

    Extend with any additional fields that you need to inform your API how
    and what to fetch.

    Management of persisting these is left to the specific platform
    (i.e. CLI or HMA).
    """

    name: str
    enabled: bool  # Whether to fetch from this or not
    fetcher_name: str  # Fetch_api.SignalExchangeAPI.name()


class CollaborationConfigStoreBase:
    def get_all(self) -> t.List[CollaborationConfigBase]:
        """
        Get all CollaborationConfigs, already resolved to the correct type
        """
        raise NotImplementedError

    def get(self, name: str):
        """Get a specific collab config by name"""
        return next(c for c in self.get_all() if c.name == name, None)

    def get_for_api(self, api: SignalExchangeAPI) -> t.List[CollaborationConfig]:
        """
        Get all the configs for a specific API, resolved to the correct type
        """
        return [c for c in self.get_all() if c.fetcher_name == api.get_name()]