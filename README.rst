==========
easy-alert
==========

Super Simple Process Monitoring Tool.

.. image:: https://badge.fury.io/py/easy-alert.svg
   :target: http://badge.fury.io/py/easy-alert
   :alt: PyPI version

.. image:: https://travis-ci.org/mogproject/easy-alert.svg?branch=master
   :target: https://travis-ci.org/mogproject/easy-alert
   :alt: Build Status

.. image:: https://coveralls.io/repos/mogproject/easy-alert/badge.svg?branch=master&service=github
   :target: https://coveralls.io/github/mogproject/easy-alert?branch=master
   :alt: Coverage Status


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
* /bin/ps

------------
Installation
------------

* ``pip`` command may need ``sudo``

+-------------+---------------------------------------+
| Operation   | Command                               |
+=============+=======================================+
| Install     |``pip install easy-alert``             |
+-------------+---------------------------------------+
| Upgrade     |``pip install --upgrade easy-alert``   |
+-------------+---------------------------------------+
| Uninstall   |``pip uninstall easy-alert``           |
+-------------+---------------------------------------+

* Check installed version: ``easy-alert --version``

* Then, write your configuration to the file ``/etc/easy-alert/easy-alert.yml``.

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
      ssh:
        - { dynamic: "aws ec2 describe-instances --output text --query 'sort_by(Reservations[].Instances[?not_null(Tags[?Key==`Name`].Value)][].[PrivateIpAddress,Tags[?Key==`Name`].Value|[0]],&[1])'", user: ec2-user, key: ~/.ssh/your.key.pem }
        - { name: web-1, host: xxx.xxx.xxx.xxx, user: ec2-user, key: ~/.ssh/your.key.pem }
        - { name: web-2, host: yyy.example.com, user: ec2-user, key: ~/.ssh/your.key.pem }

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
    easy-alert process
    easy-alert ssh --check
    easy-alert ssh

