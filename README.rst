============
``magiclog``
============

.. image:: https://travis-ci.org/drcloud/magiclog.svg?branch=master
    :target: https://travis-ci.org/drcloud/magiclog
.. image:: https://img.shields.io/pypi/v/magiclog.svg
    :target: https://pypi.python.org/pypi/magiclog
.. image:: https://img.shields.io/pypi/dd/magiclog.svg
    :target: https://pypi.python.org/pypi/magiclog

``magiclog`` simplifies application and library logging, allowing you to use
loggers where you would use print statements without complicated setup or
logger discovery.

.. code:: python

    from magiclog import log


    def main():
        log.configure()
        log.info('Hello, INFO.')


    if __name__ == '__main__':
        main()

``magiclog`` tunes the logging config in a way that's friendlier than the
``logging`` module's basic config, without asking any more work from the
library author:

* ``from magiclog import log`` retrieves the logger for your application, using
  a little meta-programming, obviating the need to figure whether you should
  use ``__package__``, ``__name__`` or the ``sys.argv[0]``.

* When you're running your task in the background, ``magiclog`` recognizes
  this and logs to Syslog; otherwise it logs to ``stderr``.

* ``magiclog`` provides a simply one-line format for ``stderr``, with the time
  and a message, but can also log in an extended format, with logging and
  level, when requested. And ``magiclog`` always includes this information when
  logging to Syslog.

``magiclog`` only arranges to log at all when you call ``log.configure()``.
If you'd like to customize levels, you can explicitly pass them to
``log.configure()`` with the ``level=...``, ``syslog=...`` and ``stderr=...``
named parameters. Otherwise, your logger has a null handler, as described in
`Configuring Logging for a Library`_

.. _`Configuring Logging for a Library`: https://docs.python.org/2/howto/logging.html#configuring-logging-for-a-library

.. code:: python

    log.configure()

    # Same as the above.
    log.configure(level='info')

    # Use Syslog or stderr based on whether or not we're in the foreground,
    # but at debug level instead of info level.
    log.configure(level='debug')

    # Enables both channels, whether foregrounded or backgrounded.
    log.configure(syslog='info', stderr='info')

    # Enables the more verbose console logging format, with module and function
    # name information as well as time.
    log.configure(level='info', extended=True)


----------------------------------
Configuring Other Modules' Loggers
----------------------------------

The ``logger`` function in ``magiclog`` provides for logger discovery, walking
the stack and using the module or package name, or the name of the running
executable, depending on the situation. You can use ``logger`` to retrieve and
configure the loggers of other modules, too, following the same rules as your
application logger.

.. code:: python

    import magiclog
    from magiclog import log


    def main():
        # You can pass a module object or a string to ``logger``. Here, we
        # configure magiclog's own (usually not very useful) logger.
        magiclog.logger(magiclog).configure()
        # Obtain a reference to Boto3's logger and auto-configure it. The
        # logger for ``magiclog`` will print out a few things as it sets this
        # logger up.
        magiclog.logger('boto3').configure()
        log.configure()
        log.info('Hello, INFO.')


    if __name__ == '__main__':
        main()
