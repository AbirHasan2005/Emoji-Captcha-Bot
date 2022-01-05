# (c) @AbirHasan2005

import uuid


def generate_rnd_id():
    """Generate Random ID"""
    return str(uuid.uuid4().hex)
