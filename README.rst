==========
easy-alert
==========

Super Simple Process Monitoring Tool.


.. image:: https://img.shields.io/badge/license-Apache%202.0-blue.svg
   :target: http://choosealicense.com/licenses/apache-2.0/
   :alt: License

.. image:: https://badge.waffle.io/mogproject/easy-alert.svg?label=ready&title=Ready
   :target: https://waffle.io/mogproject/easy-alert
   :alt: 'Stories in Ready'

--------
Features
--------

* Monitors the number of the running processes, then send notifications.

------------
Dependencies
------------

* Python >= 2.6
* pyyaml
* ``/bin/ps``

------------
Installation
------------

(todo)

Just install via pip! (may need ``sudo``)::

    pip install easy-alert

Then, write your configuration to the file ``/etc/easy-alert/easy-alert.yml``.
See an example below.

---------------------
Configuration Example
---------------------

``/etc/easy-alert/easy-alert.yml``::

    ---
    watchers:
      process:
        - { name: syslogd, error: "=1", regexp: "^/usr/sbin/syslogd" }
        - { name: awesome batch, error: "<=3", warn: "<=2", regexp: "^/usr/local/bin/awesome arg1 arg2" }

    notifiers:
      email:
        group_id: awesome
        from_address: foo@example.com
        to_address_list: bar@example.com,baz@example.com
        smtp_server: mail.example.com
        smtp_port: 587

----------------
Quickstart Guide
----------------
(todo)

::

    easy-alert process --check

---------
Upgrading
---------
::

    pip install --upgrade easy-alert
    easy-alert --version

--------------
Uninstallation
--------------
::

    pip uninstall easy-alert

(may need ``sudo``)
