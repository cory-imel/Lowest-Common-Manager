#!/usr/bin/env python3
"""
Lowest Common Manager class. Contains the methods for the tree handling and LCA functionality

Dependecies:
    logzero
    anytree
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
        """Builds dictionary containing anytree nodes with the users Display Name as the key."""

        logger.info("Building Tree")

        tree = {}

        "TODO: use different key from the users AD Display Name"
        tree[self.root[0]] = (Node(self.root[0], parent=None))

        for manager in self.hierarchy:
            for subordinate in self.hierarchy[manager]:
                tree[subordinate[0]] = (Node(subordinate[0], parent=tree[manager[0]]))
        return tree

    @staticmethod
    def find_lca(ancestors1, ancestors2):
        """Finds the lowest common ancestor (node parent e.g. manager) of two users."""

        i = 0
        while i < len(ancestors1) and i < len(ancestors2):
            if ancestors1[i] != ancestors2[i]:
                break
            i += 1
        return ancestors1[i - 1].name

    def recurse_lca(self, tree, group, lcm):
        """Recurse the group of users to find the LCA on n-ary trees"""

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
            try:
                ancestors1 = tree[group.pop()].ancestors
            except:
                group.pop()
                return self.recurse_lca(tree, group, lcm)
            try:
                ancestors2 = tree[group.pop()].ancestors
            except:
                group.pop()
                return self.recurse_lca(tree, group, lcm)

            lcm = self.find_lca(ancestors1, ancestors2)
            return self.recurse_lca(tree, group, lcm)
