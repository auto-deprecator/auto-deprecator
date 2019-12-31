===============
Auto deprecator
===============


.. image:: https://img.shields.io/pypi/v/auto_deprecator.svg
        :target: https://pypi.python.org/pypi/auto-deprecator

.. image:: https://img.shields.io/travis/gavincyi/auto_deprecator.svg
        :target: https://travis-ci.org/gavincyi/auto-deprecator

.. image:: https://readthedocs.org/projects/auto-deprecator/badge/?version=latest
        :target: https://auto-deprecator.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status




Python decorator and command to automate deprecating components


* Free software: MIT license
* Documentation: https://auto-deprecator.readthedocs.io.


How does it work?
--------

We believe that deprecating a component in your library should work in the following ways

1. Alert the users the deprecation time

When the user calls the methods or initializes the objects which will be deprecated 
in the next version or on an expected date, the user should receive the warning of
the future deprecation but get the return in success.

.. code-block:: python

  from auto_deprecator import deprecate

  @deprecate(version='2.0.0')
  def old_hello_world():
      return print("Hello world!")

.. code-block:: python

  >>> old_hello_world()
  Hello world!
  DeprecationWarning: The function "old_hello_world" will be deprecated in version 2.0.0


2. Test as if deprecated

Before the component is deprecated, unit / integration testing should be run
to ensure the deprecation does not break the existing flow. Pass in the environment
variables in the testing to simulate that the version is deployed.

.. code-block:: console

  (bash) hello-world-app
  Hello world!
  DeprecationWarning: The function "old_hello_world" will be deprecated in version 2.0.0
   
.. code-block:: console

  (bash) DEPRECATED_VERSION=2.0.0 hello-world-app
  Traceback (most recent call last):
   ...
  RuntimeError: The function "old_hello_world" is deprecated in version 2.0.0
 

3. Automatic deprecation before release

Deprecating the functions is no longer a manual work. Every time before release,
run the command `auto-deprecate` to remove the functions deprecated in the coming
version.

.. code-block:: console

  (bash) auto-deprecate hello-world.py --deprecate-version 2.0.0
  (bash) git diff

  diff --git a/hello-world.py b/hello-world.py
  index 201e546..ec41365 100644
  --- a/hello-world.py
  +++ b/hello-world.py
  @@ -1,8 +1,2 @@
  -from auto_deprecator import deprecate
  -
   def hello_world():
        return print("Hello world!")
        -
        -@deprecate(version='2.0.0')
        -def old_hello_world():
        -    return print("Hello world!")
  
