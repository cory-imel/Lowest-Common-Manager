"""
Copyright (c) 2011, Richard Nienaber
All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
The name of 'Richard Nienaber' may not be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Dependencies:
    ldap - http://pypi.python.org/pypi/python-ldap/
    logzero
    pydot (and graphviz)
"""

import ldap
from logzero import logger
import sys
from pydot import Dot, Node, Edge


class LdapSearcher(object):

    def __init__(self, server, partDomain, user, password):

        try:
            logger.info("Connecting to LDAP")
            conn = ldap.initialize(server)
            # Unsafe, LDAP server authentication not enabled
            conn.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
            conn.set_option(ldap.OPT_REFERRALS, 0)
            conn.protocol_version = 3
            conn.set_option(ldap.OPT_X_TLS_NEWCTX, 0)
            conn.simple_bind_s(user, password)

            self.ldap = conn
            self.scope = ldap.SCOPE_SUBTREE
            self.attributes = ['directReports', 'displayName', 'title']
            self.partDomain = partDomain
        except ldap.error as e:
            logger.error(e)
            sys.exit(1)
        except Exception as e:
            logger.error(e)
            sys.exit(1)

    def search(self, base, filter=None):
        try:
            return self.ldap.search_s(base, self.scope, filter, self.attributes)
        except ldap.error as e:
            logger.error(e)
            sys.exit(1)

    def search_by_accountName(self, base, name):
        filter = '(&(objectClass=user)(sAMAccountName=' + name + '))'
        return self.search(base, filter)

    def retrieve_hierarchy(self, rootUserName, maxDepth):
        logger.info("Retrieving Hierarchy")
        try:
            root = self.search_by_accountName(self.partDomain, rootUserName)
            rootName = self.getName(root)
            visited = set([])
            reports = {}
            self.recurse_direct_reports(root, visited, reports, 0, maxDepth)
            return rootName, reports
        except Exception as e:
            logger.error(e)
            sys.exit(1)

    def getName(self, entry):
        attributes = entry[0][1]
        title = '' if not 'title' in attributes else attributes['title'][0]
        title = title.decode("utf-8")
        return attributes['displayName'][0].decode("utf-8"), title

    def recurse_direct_reports(self, entry, visited, reports, depth, maxDepth):
        if depth == maxDepth:
            return
        dn, properties = entry[0]
        if dn in visited:
            return

        visited.add(dn)

        if not 'directReports' in properties:
            return

        name = self.getName(entry)
        reports[name] = []

        for report in properties['directReports']:
            reportEntry = self.search(report.decode("utf-8"), '(objectClass=*)')
            reports[name].append(self.getName(reportEntry))
            self.recurse_direct_reports(reportEntry, visited, reports, depth + 1, maxDepth)

    def unbind_ldap(self):
        logger.info("Disconnecting from LDAP")
        try:
            self.ldap.unbind_s()
        except ldap.error as e:
            logger.error(e)
            sys.exit(1)

    def render_graph(self, root, hierarchy, args):
        logger.info("Rendering Graph")
        g = Dot()
        g.set_root(root[0])

        for manager in hierarchy:
            g.add_node(Node(manager[0], shape='box'))
            for subordinate in hierarchy[manager]:
                g.add_node(Node(subordinate[0], shape='box'))
                g.add_edge(Edge(manager[0], subordinate[0]))

        g.write_svg(args.file, args.imageType, args.layout)

    def retrieve_group_users(self, group, base):
        logger.info("Retrieving users of the group")
        filter = '(&(objectCategory=user)(memberOf=' + group + '))'
        attributes = ['displayName']
        names = []
        try:
            data = self.ldap.search_s(base, self.scope, filter, attributes)
        except ldap.error as e:
            logger.error(e)
            sys.exit(1)

        for user in data:
            if user[0] is not None:
                names.append(user[1]['displayName'][0].decode("utf-8"))

        return names