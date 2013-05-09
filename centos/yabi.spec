%define version 6.15
%define unmangled_version 6.15
%define release 1
%define webapps /usr/local/webapps
%define webappname yabiadmin
%define backendname yabibe
%define shellname yabish

# Variables used for yabiadmin django app
%define installdir %{webapps}/%{webappname}
%define buildinstalldir %{buildroot}/%{installdir}
%define settingsdir %{buildinstalldir}/defaultsettings
%define logsdir %{buildroot}/var/logs/%{webappname}
%define scratchdir %{buildroot}/var/lib/%{webappname}/scratch
%define mediadir %{buildroot}/var/lib/%{webappname}/media
%define staticdir %{buildinstalldir}/static

# Variables for yabibe
%define beinstalldir /usr/local/yabibe
%define beconfdir /etc/yabi
%define bebuildinstalldir %{buildroot}/%{beinstalldir}
%define bebuildconfdir %{buildroot}/%{beconfdir}

# Variables for yabish
%define shinstalldir /usr/local/yabish
%define shbuildinstalldir %{buildroot}/%{shinstalldir}


# Turn off brp-python-bytecompile because it makes it difficult to generate the file list
# We still byte compile everything by passing in -O paramaters to python
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

Summary: yabiadmin django webapp, yabi backend and yabi shell utility
Name: yabi
Version: %{version}
Release: %{release}
License: UNKNOWN
Group: Applications/Internet
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: x86_64
Vendor: Centre for Comparative Genomics <web@ccg.murdoch.edu.au>
BuildRequires: python-setuptools openssl-devel libevent-devel python-devel
Requires: openssl
Requires(pre): shadow-utils

%pre
getent group yabi >/dev/null || groupadd -r yabi
getent passwd yabi >/dev/null || useradd -r -g yabi -d /etc/yabi yabi

%clean
#rm -rf %{buildroot}

%description
Yabi master package, depends on yabibe, yabiadmin and yabish

%package yabiadmin
Summary: yabiadmin Django web application
Group: Applications/Internet
Requires: httpd mod_wsgi

%description yabiadmin
Django web application implementing the web front end for Yabi.

%package yabibe
Summary: yabi backend
Group: Applications/Internet
Requires: python-setuptools libevent

%description yabibe
Yabi backend

%package yabish
Summary: yabi shell
Group: Applications/Internet
Requires: python-setuptools

%description yabish
Yabi command line shell


%install

for directory in "%{settingsdir} %{staticdir} %{logsdir} {scratchdir} %{mediadir} %{bebuildconfdir}"; do
	mkdir -p $directory;
done;

# Create python prefixes for packages
mkdir -p %{buildinstalldir}/{lib,bin,include}
mkdir -p %{bebuildinstalldir}/{lib,bin,include}
mkdir -p %{shbuildinstalldir}/{lib,bin,include}

cd $CCGSOURCEDIR/yabiadmin

# Install package into the prefix
export PYTHONPATH=%{buildinstalldir}/lib
python /usr/bin/easy_install -O1 --prefix %{buildinstalldir} --install-dir %{buildinstalldir}/lib .

# Create settings symlink so we can run collectstatic with the default settings
touch %{settingsdir}/__init__.py
ln -fs ..`find %{buildinstalldir} -path "*/%{webappname}/settings.py" | sed s:^%{buildinstalldir}::` %{settingsdir}/%{webappname}.py

# Create symlinks under install directory to real persistent data directories
ln -fs /var/logs/%{webappname} %{buildinstalldir}/logs
ln -fs /var/lib/%{webappname}/scratch %{buildinstalldir}/scratch
ln -fs /var/lib/%{webappname}/media %{buildinstalldir}/media

# Install WSGI configuration into httpd/conf.d
install -D ../centos/%{webappname}.ccg %{buildroot}/etc/httpd/conf.d/%{webappname}.ccg
install -D ../centos/django.wsgi %{buildinstalldir}/django.wsgi
install -m 0755 -D ../centos/%{webappname}-manage.py %{buildroot}/%{_bindir}/%{webappname}

# At least one python package has hardcoded shebangs to /usr/local/bin/python
find %{buildinstalldir} -name '*.py' -type f | xargs sed -i 's:^#!/usr/local/bin/python:#!/usr/bin/python:'
find %{buildinstalldir} -name '*.py' -type f | xargs sed -i 's:^#!/usr/local/python:#!/usr/bin/python:'

cd $CCGSOURCEDIR/yabibe
export PYTHONPATH=%{bebuildinstalldir}/lib
python /usr/bin/easy_install -O1 --prefix %{bebuildinstalldir} --install-dir %{bebuildinstalldir}/lib .
install -m 0755 -D ../centos/yabibe-init %{buildroot}/etc/init.d/yabibe
install -m 0644 -D ../centos/yabi.conf.dist %{bebuildconfdir}/yabi.conf.dist
sed -i '3i import sys; sys.path.insert(1, "${beinstalldir}")' %{bebuildinstalldir}/bin/yabibe

cd $CCGSOURCEDIR/yabish
export PYTHONPATH=%{shbuildinstalldir}/lib
python /usr/bin/easy_install -O1 --prefix %{shbuildinstalldir} --install-dir %{shbuildinstalldir}/lib .
sed -i '3i import sys; sys.path.insert(1, "${shinstalldir}")' %{shbuildinstalldir}/bin/yabish


%post yabiadmin
mamboms collectstatic --noinput > /dev/null
# Remove root-owned logged files just created by collectstatic
rm -rf /var/logs/%{webappname}/*
# Touch the wsgi file to get the app reloaded by mod_wsgi
touch ${installdir}/django.wsgi

%files yabiadmin
%defattr(-,apache,apache,-)
/etc/httpd/conf.d/*
%{_bindir}/%{webappname}
%attr(-,apache,,apache) %{webapps}/%{webappname}
%attr(-,apache,,apache) /var/logs/%{webappname}
%attr(-,apache,,apache) /var/lib/%{webappname}

%files yabibe
%defattr(-,yabi,yabi,-)
%{beinstalldir}
%{beconfdir}
/etc/init.d/yabibe

%files yabish
%defattr(-,yabi,yabi,-)
%{shinstalldir}
