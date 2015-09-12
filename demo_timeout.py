import mwapi
import mwapi.errors

my_agent = 'mwapi demo script <ahalfaker@wikimedia.org>'
session = mwapi.Session('https://10.11.12.13',  user_agent=my_agent,
                        timeout=0.5)

print("Making a request that should hang for 0.5 seconds and then timeout.")
try:
    session.get(action="fake")
except mwapi.errors.TimeoutError as e:
    print(e.__class__.__name__, str(e))
