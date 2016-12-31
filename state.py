import random
import string 
state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
print state 