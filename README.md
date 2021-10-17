# Smol.Party

A simple event planner alternative to FB Events that doesn't require logins.

[https://smol.party]("https://smol.party")


## How to dev

By default, if you don't set a `GOOGLE_CLOUD_PROJECT`, then `settings.py` will
assume you're doing local development and connect to a `db.sqlite3` file.

1. `make setup`
2. `make up`

## Future Work

* Text integration
* Email integration
* Slack integeration
* Managing your event an emailed/texted secret URL
* Managing your RSVP via an emailed/texted secret URL
* Better location picking (show the map while defining the event)
* Better date-picking
* WYSIWYG event creation form
* Event banner images
* Comments along with your RSVP
