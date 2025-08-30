django-forwardemail Documentation
===================================

Django integration for ForwardEmail API with multi-site support.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   self

Overview
--------

django-forwardemail is a Django package that provides seamless integration with the ForwardEmail service. It offers:

* **Multi-Site Support**: Full Django Sites framework integration
* **Enhanced Site Detection**: Automatic fallback mechanisms for missing request/site parameters
* **Backward Compatibility**: Maintained EmailService alias for seamless integration
* **Professional Logging**: Comprehensive logging instead of debug prints
* **ForwardEmail API**: Complete integration with ForwardEmail service

Quick Start
-----------

Install the package:

.. code-block:: bash

   pip install django-forwardemail

Add to your Django settings:

.. code-block:: python

   INSTALLED_APPS = [
       # ... other apps
       'django_forwardemail',
   ]

Use the service:

.. code-block:: python

   from django_forwardemail.services import EmailService

   EmailService.send_email(
       to='user@example.com',
       subject='Welcome!',
       text='Welcome to our service!',
       html='<h1>Welcome to our service!</h1>',
   )

Requirements
------------

* Django 4.2+
* Python 3.8+
* ForwardEmail account and API key

Links
-----

* **PyPI**: https://pypi.org/project/django-forwardemail/
* **GitHub**: https://github.com/Pacficient-Labs/django-forwardemail
* **Issues**: https://github.com/Pacficient-Labs/django-forwardemail/issues

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
