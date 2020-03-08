# Lowest-Common-Manager

Finds the lowest common manager of a group of users in an LDAP tree

Note: If you specify an image output file the application requires graphviz to be installed.


Usage: main.py [-h] --server SERVER --user USER [--password PASSWORD] --root
               ROOT [--file FILE] --group GROUP [--depth DEPTH]
               [--imageType IMAGETYPE] [--layout LAYOUT] [--version]

Example:
               
$ python main.py -s ldaps://ldap.example.com  -u CN=ldap,CN=Users,DC=ldap,DC=example,DC=com -r some.user -f graph.svg -i svg -g CN=SomeGroup,OU=Groups,OU=Corp,DC=ldap,DC=example,DC=com               
