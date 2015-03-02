#!/usr/bin/env python

'''Load the latest update for a Twitter user and leave it in an XHTML fragment'''

__author__ = 'dewitt@google.com'

import codecs
import getopt
import sys
import twitter
import config

TEMPLATE = """
<div class="twitter">
  <span class="twitter-user"><a href="http://twitter.com/%s">Twitter</a>: </span>
  <span class="twitter-text">%s</span>
  <span class="twitter-relative-created-at"><a href="http://twitter.com/%s/statuses/%s">Posted %s</a></span>
</div>
"""


def Usage():
    print 'Usage: %s [options] twitterid' % __file__
    print
    print '  This script fetches a users latest twitter update and stores'
    print '  the result in a file as an XHTML fragment'
    print
    print '  Options:'
    print '    --help -h : print this help'
    print '    --output : the output file [default: stdout]'


def FetchTwitter(user):
    assert user
    statuses = config.api.GetUserTimeline(screen_name=user, count=1, since_id=0)
    if len(statuses):
        s = statuses[0]
        xhtml = TEMPLATE % (s.user.screen_name, s.text, s.user.screen_name, s.id, s.relative_created_at)
        return xhtml

def main():
    try:
        opts, args = getopt.gnu_getopt(sys.argv[1:], 'ho', ['help', 'output='])
    except getopt.GetoptError:
        Usage()
        sys.exit(2)
    try:
        user = args[0]
    except:
        Usage()
        sys.exit(2)
    output = None
    for o, a in opts:
        if o in ("-h", "--help"):
            Usage()
            sys.exit(2)
        if o in ("-o", "--output"):
            output = a
    print FetchTwitter(user)


if __name__ == "__main__":
    main()
