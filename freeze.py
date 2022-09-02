from flask_frozen import Freezer

import app

freezer = Freezer(app.app)

@freezer.register_generator
def episode():
    for ep in app.get_eps():
        yield {'date': ep}


@freezer.register_generator
def guest():
    for ep, description in app.get_eps().items():
        if description['guests'] is None:
            continue
        for guest in description['guests'].split(", "):
            yield {'name': guest}

freezer.freeze()
