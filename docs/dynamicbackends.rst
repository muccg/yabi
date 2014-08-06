.. _dynamicbackends:

Dynamic Backends
================

Dynamic Backends are backends that are created automatically by Yabi before running a job.

Tools can be configured to run on Dynamic Backends. When Yabi is about to run a Job of a tool
that has been configured with a Dynamic Backend it will automatically create the server, it will
run the Job, then it will destroy the server. The servers are created based on dynamic backend
configurations created using Yabi admin.

Currently only AWS EC2 instances (both On-Demand and Spot) are supported, but we plan on adding
support for more providers.

AWS Credentials
---------------

The AWS credentials used to create your AWS EC2 instances have to be provided to Yabi.

Please set the ``aws_access_key_id`` and the ``aws_secret_access_key`` in your environment or config file for prod as described in :ref:`settings`.

Dynamic Backends in Admin
-------------------------

Dynamic Backends are created in Admin similarly to other Backends in Admin.
The differences are that you have to mark the Backend dynamic by checking the ``Dynamic backend`` checkbox and you have to choose a ``Dynamic backend configuration``. The ``Dynamic backend configuration`` will be used to create the Dynamic Backend.

The hostname of the backend can't be know at this time, because it will be assigned dynamically on creation. Therefore it is recommended set ``Hostname`` to ``DYNAMIC``.

Dynamic Backend Configurations
------------------------------

Dynamic Backend Configuration have to be created through Yabi Admin. These are named configuration
parameters used by Yabi when creating a Dynamic Backend.

Please edit them under Yabi/DynamicBackendConfigurations in Yabi Admin.

::
    Name            The name of the configuration (ex. "CCG AWS t1.micro")
    Configuration   A JSON dictionary containing the provider specific configuration.

The JSON configuration will always have to contain at least the ``instance class`` parameter, that specifies the type of the instance. Currently, only ``ec2`` and ``ec2spot`` are supported. Use ``ec2`` for AWS On-Demand instances and ``ec2-spot`` for AWS Spot instances.

AWS specific configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^

The following configuration parameters are currently supported for AWS instances.

======================  =============
Field                    Description
======================  =============
 region                  The AWS region
 ami_id                  The id of the AMI image
 size_id                 The instance type
 keypair_name            Name of the SSH key
 security_group_names    List of Security groups
 spot_price              (Spot Instance Only) The max price your willing to pay for an hour of usage
======================  =============

An example for an AWS Spot instance configuration:

::
 {
    "instance_class": "ec2spot",

    "spot_price": "0.08",

    "region": "ap-southeast-2",
    "ami_id": "ami-3f821e05",
    "size_id": "t1.micro",

    "keypair_name": "ccg-syd-staging",

    "security_group_names": [
        "default",
        "ssh",
        "proxied",
        "rdsaccess"
    ]
 }

An example for an AWS On-Demand instance configuration:

::
 {
    "instance_class": "ec2",

    "region": "ap-southeast-2",
    "ami_id": "ami-3f821e05",
    "size_id": "t1.micro",

    "keypair_name": "ccg-syd-staging",

    "security_group_names": [
        "default",
        "ssh",
        "proxied",
        "rdsaccess"
    ]
 }

The only difference between the two configuration is the ``instance_class``
(``ec2`` vs. ``ec2spot``) and there is no ``spot_price`` for the On-Demand instance.
