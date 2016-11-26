import getpass
import sys

from .errors import ClientInteractionRequest


def do_login(session, for_what):
    username, password = request_username_password(for_what)
    try:
        session.login(username, password)
    except ClientInteractionRequest as cir:
        params = request_interaction(cir)
        session.continue_login(cir.login_token, **params)


def request_interaction(cir):
    sys.stderr.write("{0}\n".format(cir.message))

    params = {}
    for req_doc in cir.requests:
        # sys.stderr.write("id: {0}\n".format(req_doc['id']))
        for name, field in req_doc['fields'].items():
            prefix = "{0}({1}): ".format(field['label'], name)
            if field['sensitive']:
                value = getpass.getpass(prefix)
            else:
                sys.stderr.write(prefix)
                sys.stderr.flush()
                value = open('/dev/tty').readline().strip()

            params[name] = value

    return params


def request_username_password(for_what):
    sys.stderr.write("Log into " + for_what + "\n")
    sys.stderr.write("Username: ")
    sys.stderr.flush()
    return open('/dev/tty').readline().strip(), getpass.getpass("Password: ")
