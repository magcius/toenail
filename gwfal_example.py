
from gwfal import *

with get('/'):
    respond('Welcome to the GWFAL test server.\n<br/>\n')
    respond('Try saying hello <a href="/hello">here</a>!')

with get('/hello'):
    respond("Hello %s!" % (request.name or "Jasper"))
