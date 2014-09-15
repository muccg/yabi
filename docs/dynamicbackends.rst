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

OpenStack Credentials
---------------------

Similarly, to create OpenStack Nova instances you will have to provide your OpenStack credentials used to create those instances.

Please set the ``openstack_user`` and the ``openstack_password`` in your environment or config file for prod as described in :ref:`settings`.

Dynamic Backends in Admin
-------------------------

Dynamic Backends are created in Admin similarly to other Backends in Admin.
The differences are that you have to mark the Backend dynamic by checking the ``Dynamic backend`` checkbox and you have to choose a ``Dynamic backend configuration``. The ``Dynamic backend configuration`` will be used to create the Dynamic Backend.

The hostname of the backend can't be know at this time, because it will be assigned dynamically on creation. Therefore it is recommended set ``Hostname`` to ``DYNAMIC``.

Dynamic Backend Configurations
------------------------------

Dynamic Backend Configuration have to be created through Yabi Admin. These are named configuration
parameters used by Yabi when creating a Dynamic Backend.

Please edit them under Yabi/DynamicBackendConfigurations in Yabi Admin::

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

An example for an AWS Spot instance configuration::

 {
    "instance_class": "ec2spot",

    "spot_price": "0.08",

    "region": "ap-southeast-2",
    "ami_id": "ami-3f821e05",
    "size_id": "t1.micro",

    "keypair_name": "ccg-syd-staging",

    "security_group_names": [
        "default",
        "ssh"
    ]
 }

An example for an AWS On-Demand instance configuration::


 {
    "instance_class": "ec2",

    "region": "ap-southeast-2",
    "ami_id": "ami-3f821e05",
    "size_id": "t1.micro",

    "keypair_name": "ccg-syd-staging",

    "security_group_names": [
        "default",
        "ssh"
    ]
 }

The only difference between the two configuration is the ``instance_class``
(``ec2`` vs. ``ec2spot``) and there is no ``spot_price`` for the On-Demand instance.

OpenStack specific configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The following configuration parameters are currently supported for OpenStack Nova instances.

======================  ============  =============
Field                    Mandatory?    Description
======================  ============  =============
 auth_url                   Yes        The keystone URL used for authentication
 auth_version               No         Apache Libcloud auth_version. Default is "2.0_password"
 tenant                     Yes        Tenant name
 service_type               No         Catalog entry for service type. Default is "compute"
 service_name               No         Catalog entry for service name. Default is "nova"
 service_region             No         Catalog entry for service region. Default is "RegionOne"
 flavor                     Yes        Flavor of the instance
 image_name                 Yes        Name of image to boot the instance from
 keypair_name               Yes        Name of the SSH key to install into the instance
 availability_zone          No         The zone you would like your instance to be created in
 security_group_names       No         List of Security groups
======================  ============  =============

An example would be the following configuration that it is used to start up `NeCTAR`_ instances::

 {
    "instance_class": "nova",
    "auth_url": "https://keystone.rc.nectar.org.au:5000/v2.0/tokens/",
    "tenant": "pt-8173",
    "service_region": "Melbourne",
    "service_name": "Compute Service",

    "availability_zone": "tasmania",
    "flavor": "m1.small",
    "image_name": "NeCTAR Ubuntu 14.04 (Trusty) amd64",
    "keypair_name": "tszabo",
    "security_group_names": [
        "default", "ssh", "icmp"
    ]
 }

.. _`NeCTAR`: http://nectar.org.au/
