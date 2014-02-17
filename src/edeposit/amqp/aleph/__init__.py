#! /usr/bin/env python
# -*- coding: utf-8 -*-
# This package may contain traces of nuts
from collections import namedtuple


import aleph
import marcxml
import convertors


from .. import AMQPMessage


###############################################################################
# Add new record to Aleph #####################################################
###############################################################################
#
## Aleph's data wrappers ######################################################
class Author(namedtuple("Author", ['firstName', 'lastName', 'title'])):
    pass


class Producent(namedtuple("Producent",
                           ['title',
                            'phone',
                            'fax',
                            'email',
                            'url',
                            'identificator',
                            'ico'])):
    pass


class EPublication(namedtuple("EPublication",
                              ['nazev',
                               'podnazev',
                               'vazba',
                               'cena',
                               'castDil',
                               'nazevCasti',
                               'nakladatelVydavatel',
                               'datumVydani',
                               'poradiVydani',
                               'zpracovatelZaznamu',
                               'kategorieProRIV',
                               'mistoDistribuce',
                               'distributor',
                               'datumDistribuce',
                               'datumProCopyright',
                               'format',
                               'url',
                               'mistoVydani',
                               'ISBNSouboruPublikaci',
                               'autori',
                               'originaly'])):
    """
    see https://e-deposit.readthedocs.org/cs/latest/dm01.html
    """
    pass


class OriginalFile(namedtuple("OriginalFile",
                              ['url', 'format', 'file', 'isbns'])):
    """ type of isbn: ISBN"""
    pass


## Protocol query wrappers ####################################################
class AlephExport(namedtuple("AlephExport",
                             ['epublication',
                              'linkOfEPublication'])):
    """ epublication ... type of EPublication
    linkOfEPublication  ... url with epublication

    User will fill this record.
    """
    pass


class ExportRequest(namedtuple("ExportRequest",
                               ['export',
                                'UUID'])):
    pass


class AlephExportResult(namedtuple("AlephExportResult",
                                   ['docNumber',
                                    'base',
                                    'xml',
                                    'success',
                                    'message'])):
    """ docNumber ... docNumber of a record in Aleph
    base      ... base of Aleph
    success   ... whether import was successfull
    message   ... message of error or success
    """
    pass


class ExportResult(namedtuple("ExportResult",
                              ['result',
                               'UUID'])):
    """
    ... result is type of AlephExportResult
    ... UUID is UUID used in ExportRequest
    """
    pass


###############################################################################
# Search Aleph ################################################################
###############################################################################
"""
Workflow is pretty simple:

To query Aleph, just create one of the Queries - ISBNQuery for example and put
it into SearchRequest wrapper with UUID. Then encode it by calling 
toAMQPMessage() and send the message to the Aleph exchange.

---
isbnq = ISBNQuery("80-251-0225-4")
request = SearchRequest(isbnq, UUID)

amqp.send(
    toAMQPMessage(request)
    "ALEPH'S_EXCHANGE"
)
---

and you will get back AMQP message, and after decoding with fromAMQPMessage()
also SearchResult.

If you want to just get count of how many items is there in Aleph (you should
use this instead of just calling len() to SearchResult.records - it doesn't put
that much load to Aleph), just wrap the ISBNQuery with CountQuery:

---
isbnq = CountQuery(ISBNQuery("80-251-0225-4"))
# rest is same..
---

and you will get back (after decoding) CountResult.
"""

class AlephRecord(namedtuple("AlephRecord",
                             ['library',
                              'docNumber',
                              'xml',
                              'epublication'])):
    pass


class SearchResult(namedtuple("SearchResult",
                              ['records',
                               'UUID'])):
    pass
    """ result of search request """


class CountResult(namedtuple("CountResult",
                             ['num_of_records',
                              'UUID'])):
    pass


class GenericQuery(namedtuple("GenericQuery",
                              ['base',
                               'phrase',
                               'considerSimilar',
                               'field'])):
    """
    base ... base in Aleph
    NKC, ...
    see:  http://aleph.nkp.cz/F/?func=file&file_name=base-list
    """
    pass


class _QueryTemplate:
    """
    This class is here to just save some effort by using common ancestor with
    same .getSearchResult() and .getCountResult() definition.
    """
    def getSearchResult(self, UUID):
        records = []
        for doc_id, library in self._getIDs():
            xml = aleph.downloadAlephDocument(doc_id, library)

            records.append(
                AlephRecord(
                    library,
                    doc_id,
                    xml,
                    convertors.toEPublication(xml)
                )
            )

        return SearchResult(records, UUID)

    def getCountResult(self, UUID):
        return CountResult(
            self._getCount(),
            UUID
        )


class ISBNQuery(namedtuple("ISBNQuery", ["ISBN"]), _QueryTemplate):
    def _getIDs(self):
        return aleph.getISBNsIDs(self.ISBN)

    def _getCount(self):
        return aleph.getISBNCount(self.ISBN)


class AuthorQuery(namedtuple("AuthorQuery", ["author"]), _QueryTemplate):
    def _getIDs(self):
        return aleph.getAuthorsBooksIDs(self.author)

    def _getCount(self):
        return aleph.getAuthorsBooksCount(self.author)


class PublisherQuery(namedtuple("PublisherQuery", ["publisher"]), _QueryTemplate):
    def _getIDs(self):
        return aleph.getPublishersBooksIDs(self.publisher)

    def _getCount(self):
        return aleph.getPublishersBooksCount(self.publisher)


class CountQuery(namedtuple("CountQuery", ["type"])):
    """
    Put one of the Queries to .type properties and it will return just number
    of records, instead of records itself.
    """
    pass


class SearchRequest(namedtuple("SearchRequest",
                               ['query',
                                'UUID'])):
    """
    query -- GenericQuery, ISBNQuery, .. *Query
    UUID -- identification of a query in a result response
    """


###############################################################################
#  Interface for an external world  ###########################################
###############################################################################
def toAMQPMessage(request):
    """ returns  edeposit.amqp.AMQPMessage """

    return AMQPMessage(
        data=convertors.toJSON(request),
        headers="",
        properties=""
    )


def fromAMQPMessage(message):
    """ returns message of given type
    message       is type of edeposit.amqp.AMQPMessage
    returns structure depending on data in message.
    """
    return convertors.fromJSON(message.body)


def send_response(response):
    raise NotImplementedError("send_response() is not yet implemented.")


def reactToAMQPMessage(message):
    decoded = fromAMQPMessage(message)

    if type(decoded) != SearchRequest:  # TODO: pridat podporu exportnich typu
        raise ValueError("Unknown type of message: '" + type(decoded) + "'!")

    query = decoded.query

    response = None
    if type(query) == CountQuery:
        # process count query
        pass
    elif type(query) == ISBNQuery:
        response = SearchResult(
            records=map(
                lambda id_n, library:
                    aleph.downloadAlephDocument(id_n, library),
                aleph.getISBNsIDs(query.ISBN)
            ),
            UUID=decoded.UUID
        )
    elif type(query) == AuthorQuery:
        response = SearchResult(
            records=map(
                lambda id_n, library:
                    aleph.downloadAlephDocument(id_n, library),
                aleph.getAuthorsBooksIDs(query.Author)
            ),
            UUID=decoded.UUID
        )


    if response is not None:
        send_response(response)

if __name__ == '__main__':
    a = ISBNQuery("80-251-0225-4")
    print a.getSearchResult("xex")

    print "ahoj"
