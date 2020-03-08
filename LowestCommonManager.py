#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Cory Imel"
__version__ = "0.1.0"
__license__ = "MIT"


from logzero import logger
from anytree import Node


class LowestCommonManager(object):

    def __init__(self, hierarchy, root, group):

            self.hierarchy = hierarchy
            self.root = root
            self.group = group

    def build_tree(self):

        logger.info("Building Tree")

        tree = {}

        tree[self.root[0]] = (Node(self.root[0], parent=None))

        for manager in self.hierarchy:
            for subordinate in self.hierarchy[manager]:
                tree[subordinate[0]] = (Node(subordinate[0], parent=tree[manager[0]]))
        return tree

    def find_lca(self, ancestors1, ancestors2):

        i = 0
        while i < len(ancestors1) and i < len(ancestors2):
            if ancestors1[i] != ancestors2[i]:
                break
            i += 1
        return ancestors1[i - 1].name

    def recurse_lca(self, tree, group, lcm):

        if lcm is self.root[0]:
            return self.root[0]

        if len(group) is 1:

            if lcm is tree[group[0]].parent.name:
                return lcm

            ancestors1 = tree[group[0]].ancestors
            ancestors2 = tree[lcm].ancestors
            return self.find_lca(ancestors1, ancestors2)

        elif len(group) is 2:

            ancestors1 = tree[group[0]].ancestors
            ancestors2 = tree[group[1]].ancestors
            return self.find_lca(ancestors1, ancestors2)

        else:

            ancestors1 = tree[group.pop()].ancestors
            ancestors2 = tree[group.pop()].ancestors
            lcm = self.find_lca(ancestors1, ancestors2)
            return self.recurse_lca(tree, group, lcm)
