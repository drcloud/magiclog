============
``magiclog``
============


Printing log messages is easy but it makes certain kinds of integrations hard:

* Logging to Syslog requires redirection,

* Including the module or function name is tedious,

* Printing time information at the console requires forethought.

Loggers make these things easy; but configuration is hard. ``magiclog`` does
the right thing for libraries, command line tools and simple scripts. It's as
easy as:

.. code:: python

    from magiclog import log


    def main():
        log.configure()
        log.info('Hello, INFO.')


    if __name__ == '__main__':
        main()

If your application is started from the console, ``magiclog`` logs to
``stderr``. If it's started without a terminal attached -- as would be the
case with a cron job or web server -- it logs to Syslog. You can tune the
default level, or the level for either or both of ``stderr`` or ``syslog``,
with named arguments to ``configure``.


----------------------------------
Configuring Other Modules' Loggers
----------------------------------

The ``logger`` function in ``magiclog`` is how it finds the right logger for
the module it's imported into, walking the stack and using the module or
package name, or the name of the running executable, depending on the
situation. You can use ``logger`` to retrieve and configure the loggers of
other modules, too.

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
