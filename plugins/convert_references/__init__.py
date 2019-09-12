def build_filter(args):
    return Filter(args)

import re, sys
from internal import rev_number_to_git_hash, rev_hash_to_git_hash

class Filter:
    def __init__(self, args):
        #self.logFile = "/tmp/convert_references"
        self.logFile = None
        if self.logFile is not None:
            with open(self.logFile, "w") as output:
                output.write('')

        self.hashre = re.compile (r"\b(?P<ref>[0-9a-fA-F]{6,50})\b")
        self.revre = re.compile (r"\b(r(ev(ision)?)?|(?P<keep>backport(ing)?|commit))\s*(?P<ref>[0-9]+)\b")

        self.bugs_and_prs_re = [
                (re.compile ("bugs (?P<ref1>\d+) and (?P<ref2>\d+)"), "bugs #{ref1} and #{ref2}"),
                (re.compile ("([Bb]ug) (?P<ref>\d+)"), "bug #{ref}"),
                (re.compile ("http://eigen.tuxfamily.org/bz/show_bug.cgi\?id=(?P<ref>\d+)"), "#{ref}"),
                (re.compile ("[Pp]ull [Rr]equest #(?P<ref>\d+)"), "pull request PR-{ref}"),
                (re.compile ("PR #(?P<ref>\d+)"), "PR-{ref}"),
                ]

        # When no 'rev', 'r', 'revision' is prepent to the revision number,
        # it is fairly hard to recognize revision number...
        # regex = re.compile (r'\w\s+\b(?P<ref>[0-9]{3,})\b')
        # TODO Catch ranges of revision numbers. 12543-31245

    def convert (self, desc, regex, replacement, db, startswith=True, output=None):
        """
        - regex, desc Argument to re.finditer
        - replacement arguments passed to re.MacthObject.expand
        - db dictionnary whose pairs (key, value) are used to replace the reference
        """
        if len(db) == 0:
            return desc, False
        newdesc = ""
        i = 0

        assert "ref" in regex.groupindex

        N = 0
        for match in re.finditer (regex, desc):
            ref = match.group('ref')
            found = False
            if startswith:
                for oldref, nr in db.iteritems():
                    if oldref.startswith (ref):
                        found = True
                        newref = nr
                        break
            else:
                if ref in db:
                    newref = db[ref]
                    found = True
            if found:
                groups = dict(match.groupdict())
                for k,v in groups.iteritems():
                    if v is None: groups[k] = ""
                groups["newref"] = newref
                newdesc += desc[i:match.start()] + replacement.format (**groups)
                N += 1
                #if output is not None: output.write ("=== Success\n%s:%s\n\n==>%s\n%s===\n""" % (ref, desc, newref, ", ".join (db.keys())))
            else:
                if output is not None: output.write ("===\nCould not find %s from\n%s\n===\n""" % (ref,desc))
                newdesc += desc[i:match.end()]

            i = match.end()
        newdesc += desc[i:]

        if N>0 and output is not None: output.write ("=== Converted:\n%s\n==>\n%s\n===\n""" % (desc, newdesc))
        return newdesc, N>0

    def convertBugsAndPrs (self, desc, regex, replacement, output=None):
        """
        - regex, desc Argument to re.finditer
        - replacement arguments passed to re.MacthObject.expand
        """
        newdesc = ""
        i = 0

        for match in re.finditer (regex, desc):
            groups = dict(match.groupdict())
            for k,v in groups.iteritems():
                if v is None: groups[k] = ""
            newdesc += desc[i:match.start()] + replacement.format (**groups)
            #if output is not None: output.write ("=== Success\n%s:%s\n\n==>%s\n%s===\n""" % (ref, desc, newref, ", ".join (db.keys())))
            i = match.end()
        newdesc += desc[i:]

        return newdesc

    def commit_message_filter(self,commit_data):
        with open(self.logFile if self.logFile is not None else "/dev/null", "a") as output:

            desc = commit_data["desc"]

            # First look for revisions
            desc, has_rev  = self.convert (desc, self.revre , "{keep}{newref}", rev_number_to_git_hash, startswith=False, output=output)
            desc, has_hash = self.convert (desc, self.hashre,       "{newref}", rev_hash_to_git_hash  , startswith=True , output=output)

            for regex, replacement in self.bugs_and_prs_re:
                desc = self.convertBugsAndPrs (desc, regex, replacement, output=output)

            #if not has_rev and not has_hash:
                #if output is not None: output.write ("===\nNothing in %s\n===\n""" % (commit_data['desc'],))
            commit_data["desc"] = desc
