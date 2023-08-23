from core.settings import (
    settings, )
import os


# generated by running: openssl rand -hex 128
JWT_SECRET_KEY = settings.JWT_SECRET_KEY
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 131400

ROOT_TOKEN = '1c241675-504e-4329-9e11-eb3b16957347'
RADIUS_BASE_URL = 'http://178.79.149.74/cake3/rd_cake'

PAYSTACK_BASE_URL = 'https://api.paystack.co'
RAVE_BASE_URL = 'https://api.flutterwave.com/v3'


PAYSTACK_SECRET_KEY = 'sk_live_8d8995dcc919b6192e293cee37d38957406afe07'
#'sk_test_aa42a0cb8fd68d54ccec0650b5007fb933a6e6aa'  #'sk_live_8d8995dcc919b6192e293cee37d38957406afe07'
PAYSTACK_PUBLIC_KEY = 'pk_live_56cb9e2123f3af45c6560a898e8aba2c68a149a9'
#'pk_test_331dfbcb75f2b97887e46a0b7c24d01bc8840d26'
#'pk_live_56cb9e2123f3af45c6560a898e8aba2c68a149a9'
RAVE_TEST_PUBK_KEY = 'FLWPUBK_TEST-a6f1e5988bba4d9f525c6402d499724f-X'
RAVE_TEST_SECK_KEY = 'FLWSECK_TEST-bfb9ebd7b003abf2c1b9466080959c75-X'

RAVE_LIVE_PUBK_KEY = 'FLWPUBK-1ae6d9a5162fb7454898e687eef7f948-X'
RAVE_LIVE_SECK_KEY = 'FLWSECK-37f82bc21c1d482a87dfc189dc54f888-188dee67e07vt-X'