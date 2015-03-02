import config
import os
import tornado
import tornado.httpserver
import twitter
import requests
from tornado.options import define, options
from tornado.web import RequestHandler, Application


define('debug', default=1, help='hot deployment. use in dev only', type=int)
define('port', default=8888, help='run on the given port', type=int)


# get latest tweets of a user examples
# taken from  https://github.com/bear/python-twitter/blob/master/examples/twitter-to-xhtml.py.

TEMPLATE = """
    <div class="twitter">
    <span class="twitter-user"><a href="http://twitter.com/%s">Twitter</a>: </span>
    <span class="twitter-text">%s</span>
    <span class="twitter-relative-created-at"><a href="http://twitter.com/%s/statuses/%s">Posted %s</a></span>
    </div>
  """
REDIS_TWEETS = 'tagos:tweets'

def formatTweet(tweet):
    xhtml = TEMPLATE % (s.user.screen_name, s.text, s.user.screen_name, s.id, s.relative_created_at)
    return xhtml

def fetchTwitter(user):
    assert user
    timelineUrl = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    statuses = config.api.GetUserTimeline(screen_name=user, count=5, since_id=0)
    import pdb; pdb.set_trace()
    for status in statuses:
        config.redisLabsConn.zadd(REDIS_TWEETS, status.id, status.text)
    if len(statuses):
        s = statuses[0]
    return formatTweet(s)

def fetchTweets(user):
    assert user
    latestTweet = config.redisLabsConn.zrevrange(REDIS_TWEETS, 0, 1)
    if latestTweet: # and latestTweet[0].relative_created_at:
        return formatTweet(latestTweet)
    else:
        return fetchTwitter(user)

class LatestTweetHandler(RequestHandler):
    def get(self, twitterHandle='softwarmechanic'):
        return fetchTweets(twitterHandle)

class Application(Application):
    def __init__(self):
        handlers = [
                (r'/', LatestTweetHandler),
                ]
        settings = dict(
            autoescape=None,  # tornado 2.1 backward compatibility
            debug=options.debug,
            gzip=True,
            xheaders=True,

            )
        tornado.web.Application.__init__(self, handlers, **settings)

def main():
    tornado.options.parse_command_line()
    App = Application()
    httpserver = tornado.httpserver.HTTPServer(App)
    httpserver.listen(port=options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
