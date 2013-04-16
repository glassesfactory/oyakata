oyakata
==========

oyakata is Simple process manager.
manage process from Procfile !!

inspired [gaffer](https://github.com/benoitc/gaffer)

Install
----------------

`pip install oyakata`


Workflow
----------------

1. Launch Oyakata Daemon
	`oyakatad -c /path/to/oyakata.toml --daemon`
2. use oyakata to manage your process.
	`oyakata load`

Usage Oyakata
----------------------

####Load Procfile and running.

`oyakata load`

####Unload Procfile and stop application.

`oyakata unload`


Launch Oyakata
---------------------

###upstart
[oyakata.conf](http://gist)

