# A centos instance for building RPM packages
node default {
<<<<<<< HEAD
  $custom_hostname = 'aws-rpmbuild-centos6.ec2.ccgapps.com.au'
  include role::rpmbuild::sydney
=======
  include role::rpmbuild
>>>>>>> 909d81c7f7953a3bfadeb5c0525f54e0cac24b48
}
