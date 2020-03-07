#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Cory Imel"
__version__ = "0.1.0"
__license__ = "MIT"

import argparse
import getpass
import re
from logzero import logger
from LDAPSearcher import LdapSearcher
from LowestCommonManager import LowestCommonManager


def main(args):

    # group = ['Stella Wiley', 'Ronni Ko', "Bob Johnson"]

    domain = re.search('ldaps://((.*\.?)+)', args.server)
    split = domain.groups()[0].split('.')[1:]
    partDomain = 'dc=' + ',dc='.join(split)

    searcher = LdapSearcher(args.server, partDomain, args.user, args.password)
    root, hierarchy = searcher.retrieve_hierarchy(args.root, args.depth)
    group = searcher.retrieve_group_users(args.group)
    lcm = LowestCommonManager(hierarchy, root, group)
    tree = lcm.build_tree()

    if args.file is not '':
        searcher.render_graph(root, hierarchy, args)

    searcher.unbind_ldap()
    logger.info("Starting Search")
    print(lcm.recurse_lca(tree, group, lcm=''))


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--server', '-s', help='The FQDN of the ldap server e.g. ldap://domain.server.com',
                        required=True)
    parser.add_argument('--user', '-u', help='The user to log into the ldap server with e.g. user@domain.server.com',
                        required=True)
    parser.add_argument('--password', '-p', help='LDAP user password.', default='')
    parser.add_argument('--root', '-r', help='The root user''s login name e.g. name.surname', required=True)
    parser.add_argument('--file', '-f', help='The file to output to e.g. c:\chart.png', default='')
    parser.add_argument('--group', '-g', help='The group in x509 format e.g. CN=IT,OU=Groups,DC=example,DC=com',
                        required=True)
    parser.add_argument('--depth', '-d', type=int, default=max,
                        help='The amount of levels to represent in the hierarchy.')
    parser.add_argument('--imageType', '-i', help='An image type understood by GraphViz e.g. png, svg, etc.',
                        default='svg')
    parser.add_argument('--layout', '-l', help='A layout type understood by GraphViz e.g. dot, neato, circo, etc.')
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()

    if args.password is '':
        args.password = getpass.getpass("Password: ", stream=None)

    main(args)
