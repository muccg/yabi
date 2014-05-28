# A centos instance for building RPM packages
node default {
  include ccgcommon
  include ccgcommon::source
  include python
  include repo::epel
  include repo::ius
  include repo::pgrpms

  file { '/usr/local/src':
    ensure => directory,
    mode   => '0777',
  }
}
