# Copyright (c) Facebook, Inc. and its affiliates. All Rights Reserved

import datetime
import os
import random
import string
from hmalib.common.logging import get_logger
from hmalib.common.timebucketizer import TimeBucketizer
from hmalib.common.models.pipeline import HashRecord

logger = get_logger(__name__)

BUCKET_WIDTH = datetime.timedelta(minutes=10)


def lambda_handler(event, context):
    """
    explanation here.
    """
