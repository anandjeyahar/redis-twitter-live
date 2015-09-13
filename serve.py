import config
import os
import tornado
import tornado.httpserver
import twitter
import requests
import redis
from tornado.options import define, options
from tornado.web import RequestHandler, Application
import json

define('debug', default=1, help='hot deployment. use in dev only', type=int)
define('port', default=8889, help='run on the given port', type=int)


# get latest tweets of a user examples
# taken from
# https://github.com/bear/python-twitter/blob/master/examples/twitter-to-xhtml.py.

redistogo_url = os.getenv('REDISTOGO_URL')
assert redistogo_url, 'No redis To Go URL set'
redisToGoConn = redis.from_url(redistogo_url)

TEMPLATE = """
    <div class="twitter">
    <span class="twitter-user"><a href="http://twitter.com/%s">Twitter</a>: </span>
    <span class="twitter-text">%s</span>
    <span class="twitter-relative-created-at"><a href="http://twitter.com/%s/statuses/%s">Posted %s</a></span>
    </div>
  """
REDIS_TWEETS = 'redis:tweets:'
EXPIRY = 7 * 24 * 3600


def formatTweet(tweet):
    xhtml = TEMPLATE % (tweet.user.screen_name, tweet.text,
                        tweet.user.screen_name, tweet.id, tweet.relative_created_at)
    return xhtml


def fetchTwitter(user):
    assert user
    timelineUrl = 'https://api.twitter.com/1.1/statuses/user_timeline.json'
    statuses = config.api.GetUserTimeline(
        screen_name=user, count=5, since_id=0)
    latestTweet = max(statuses, key=lambda k: k.id)
    redisToGoConn.setex(REDIS_TWEETS + user, EXPIRY,
                        formatTweet(latestTweet))
    if len(statuses):
        s = statuses[0]
    return formatTweet(s)


def fetchTweets(user, live=False):
    assert user
    latestTweet = config.redisLabsConn.get(
        REDIS_TWEETS + user) if not live else None
    if latestTweet:  # and latestTweet[0].relative_created_at:
        return latestTweet
    else:
        return fetchTwitter(user)


class LatestTweetHandler(RequestHandler):

    def get(self, twitterHandle='@GautamGambhir', live=False):
        self.finish(json.dumps({'tweet': fetchTweets(twitterHandle, live)}))


class Application(Application):

    def __init__(self):
        handlers = [
            (r'/([^/]+)', LatestTweetHandler),
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
