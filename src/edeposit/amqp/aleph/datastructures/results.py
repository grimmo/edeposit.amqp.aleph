#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
from collections import namedtuple


class ISBNValidationResult(namedtuple("ISBNValidationResult", ["is_valid"])):
    """
    Response to ISBNValidationRequest.

    is_valid -- bool
    """
    pass


class SearchResult(namedtuple("SearchResult", ['records'])):
    """
    This is response structure, which is sent back when SearchRequest is
    received.

    records -- array of AlephRecord structures
    """
    pass


class CountResult(namedtuple("CountResult", ['num_of_records'])):
    """
    This is returned back to client when he send CountRequest.
    """
    pass