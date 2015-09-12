import mwapi
import mwapi.errors

my_agent = 'mwapi demo script <ahalfaker@wikimedia.org>'
session = mwapi.Session('https://en.wikipedia.org',  user_agent=my_agent)

print("You should see a warning below:")
session.get(action='query', list='users|foobar', ucusers="Foo")
