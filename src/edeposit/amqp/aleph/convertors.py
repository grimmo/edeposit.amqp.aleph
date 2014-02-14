#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Interpreter version: python 2.7
#
#= Imports ====================================================================
import json
from collections import namedtuple


from marcxml import MARCXMLRecord
from __init__ import Producent, EPublication, OriginalFile, Author


#= Functions & objects ========================================================
def toEPublication(marcxml):
    """
    Convert MARCXMLRecord object to EPublication named tuple (see __init__.py).

    marcxml -- MARCXMLRecord instance OR string (with <record> tag)

    Returns EPublication named tuple.
    """
    parsed = marcxml
    if not isinstance(marcxml, MARCXMLRecord):
        parsed = MARCXMLRecord(str(marcxml))

    distributor = ""
    mistoDistribuce = ""
    datumDistribuce = ""

    # parse information about distributors
    distributors = parsed.getCorporations("dst")
    if len(distributors) >= 1:
        mistoDistribuce = distributors[0].place
        datumDistribuce = distributors[0].date
        distributor = distributors[0].name

    # zpracovatel
    zpracovatel = parsed.getDataRecords("040", "a", False)
    if len(zpracovatel) >= 1:
        zpracovatel = zpracovatel[0]
    else:
        zpracovatel = ""

    # i know, that this is not PEP8, but you dont want to see it without proper
    # formating (it looks bad, really bad)
    return EPublication(
        nazev               = parsed.getName(),
        podnazev            = parsed.getSubname(),
        vazba               = parsed.getBinding()[0],
        cena                = parsed.getPrice(),
        castDil             = parsed.getPart(),
        nazevCasti          = parsed.getPartName(),
        nakladatelVydavatel = parsed.getPublisher(),
        datumVydani         = parsed.getPubDate(),
        poradiVydani        = parsed.getPubOrder(),
        zpracovatelZaznamu  = zpracovatel,
        kategorieProRIV     = "",
        mistoDistribuce     = mistoDistribuce,
        distributor         = distributor,
        datumDistribuce     = datumDistribuce,
        datumProCopyright   = "",
        format              = parsed.getFormat(),
        url                 = "",
        mistoVydani         = parsed.getPubPlace(),
        ISBNSouboruPublikaci= parsed.getISBNs(),
        autori              = map(  # convert Persons to amqp's Authors
            lambda a: Author(
                (a.name + " " + a.second_name).strip(),
                a.surname,
                a.title
            ),
            parsed.getAuthors()
        ),
        originaly=parsed.getOriginals(),
    )


def fromEPublication(epublication):
    raise NotImplementedError("Not implemented yet.")


def _serializeNT(data):
    """
    Serialize namedtuples (and other basic types) to dictionary with special
    properties.

    Namedtuples can be later automatically de-serialized by calling
    _deserializeNT().
    """
    if isinstance(data, list):
        return map(lambda x: _serializeNT(x), data)

    elif isinstance(data, tuple) and hasattr(data, "_fields"):  # is namedtuple
        serialized = _serializeNT(dict(data._asdict()))
        serialized["__nt_name"] = data.__class__.__name__

        return serialized

    elif isinstance(data, tuple):
        return tuple(map(lambda x: _serializeNT(x), data))

    elif isinstance(data, dict):
        return dict(
            map(
                lambda key: [key, _serializeNT(data[key])],
                data.keys()
            )
        )

    return data


def toJSON(structure):
    """
    Convert structure to json.

    This is necesarry, because standard JSON module can't serialize
    namedtuples.
    """
    return json.dumps(_serializeNT(structure))


def _deserializeNT(data):
    """
    Deserialize special kinds of dicts from _serializeNT().
    """
    if isinstance(data, list):
        return map(lambda x: _deserializeNT(x), data)

    elif isinstance(data, tuple):
        return tuple(map(lambda x: _deserializeNT(x), data))

    elif isinstance(data, dict) and "__nt_name" in data:  # is namedtuple
        class_name = data["__nt_name"]
        del data["__nt_name"]

        return globals()[class_name](
            **dict(zip(data.keys(), _deserializeNT(data.values())))
        )

    elif isinstance(data, dict):
        return dict(
            map(
                lambda key: [key, _deserializeNT(data[key])],
                data.keys()
            )
        )

    elif isinstance(data, unicode):
        return data.encode("utf-8")

    return data


def fromJSON(json_data):
    """
    Convert JSON string back to python structures.

    This is necesarry, because standard JSON module can't serialize
    namedtuples.
    """
    return _deserializeNT(json.loads(json_data))