import redis
import twitter

redisLabsConn = redis.StrictRedis(host='pub-redis-19836.us-east-1-2.5.ec2.garantiadata.com',
                            port='19836',
                            db=0,
                            password='tagosTweets')

api = twitter.Api(consumer_key='oizwMCzEsrSWAUeWQ7Tvk78aM',
                  consumer_secret='UrXu4guVTzbKFRoxgF8bcvMnevZMdXWswJFXciCy41GVDCVoiB',
                  access_token_key='3042690962-hpKcZYqIHbzgKiKPvFPpHo9TV4bKBl59LM2Po8P',
                  access_token_secret='rPmXiUDWcZB3KpOyZ6igYqQL9TS0alwv3jPWPQ2127USW')
