"""
Query demonstrations
====================

This script demonstrates interesting use of the `mwapi` library to login and
query English Wikipedia's MediaWiki API.  Here's the basic flow:

1. Log in
2. Confirm logged-in status
3. Query for the last 5 revisions of User_talk:EpochFail
4. Query for these revisions by their revision ID
5. Cause the API to throw an error and catch it.

"""
import getpass
import sys
from itertools import islice

import mwapi

session = mwapi.Session('https://en.wikipedia.org')

print("Logging into English Wikipedia")
session.login(input("Username: "), getpass.getpass("Password: "))

print("whoami?")
print("\t", session.get(action='query', meta='userinfo'), "\n")


def query_revisions_by_revids(revids, batch=50, **params):

    revids_iter = iter(revids)
    while True:
        batch_ids = list(islice(revids_iter, 0, batch))
        if len(batch_ids) == 0:
            break
        else:
            doc = session.post(action='query', prop='revisions',
                               revids=batch_ids, **params)

            for page_doc in doc['query'].get('pages', {}).values():
                page_meta = {k: v for k, v in page_doc.items()
                             if k != 'revisions'}
                if 'revisions' in page_doc:
                    for revision_doc in page_doc['revisions']:
                        revision_doc['page'] = page_meta
                        yield revision_doc


def query_revisions(title=None, pageid=None, batch=50, limit=50,
                    **params):
    if title is None and pageid is None:
        raise TypeError("query_revisions requires 'title' or 'pageid'")

    params.update({
        'titles': title,
        'pageids': pageid
    })

    yielded = 0
    doc = None
    while doc is None or 'batchcomplete' not in doc:
        doc = session.post(action='query', prop='revisions',
                           rvlimit=min(batch, limit - yielded),
                           query_continue=(doc or {}).get('continue'),
                           **params)

        for page_doc in doc['query'].get('pages', {}).values():
            page_meta = {k: v for k, v in page_doc.items() if k != 'revisions'}
            if 'revisions' in page_doc:
                for revision_doc in page_doc['revisions']:
                    revision_doc['page'] = page_meta
                    yield revision_doc
                    yielded += 1
                    if yielded >= limit:
                        doc['batchcomplete'] = ""

print("Querying by title")
rev_ids = []
sys.stdout.write("\t ")
for doc in query_revisions(title="User_talk:EpochFail", rvprop="ids", limit=55):
    sys.stdout.write(".")
    sys.stdout.flush()
    rev_ids.append(doc['revid'])
sys.stdout.write("\n\n")

print("Querying by rev_id")
for doc in query_revisions_by_revids(rev_ids):
    print("\t", doc['page'], doc['revid'], doc['comment'])
print("")

print("Query with an error")
try:
    session.get(action="query", prop="revisions", revids=[123523], rvlimit=2)
except mwapi.APIError as e:
    print("\t", "An APIError was caught.")
    print("\t", e)
print("")
