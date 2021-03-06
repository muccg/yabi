%define __python /usr/bin/python%{pybasever}
# sitelib for noarch packages
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%define pyver 27
%define pybasever 2.7

%define version 9.9.5
%define unmangled_version 9.9.5
%define release 1
%define webapps /usr/local/webapps
%define webappname yabi
%define shellname yabish

# Variables used for yabi django app
%define installdir %{webapps}/%{webappname}
%define buildinstalldir %{buildroot}/%{installdir}
%define staticdir %{buildinstalldir}/static
%define logdir %{buildroot}/var/log/%{webappname}
%define scratchdir %{buildroot}/var/lib/%{webappname}/scratch
%define storedir %{buildroot}/var/lib/%{webappname}/store
%define mediadir %{buildroot}/var/lib/%{webappname}/media

# Variables for yabish
%define shinstalldir /opt/yabish
%define shbuildinstalldir %{buildroot}/%{shinstalldir}


Summary: yabi django webapp, celery backend and yabi shell utility
Name: yabi
Version: %{version}
Release: %{release}
License: GNU GPL v3
Group: Applications/Internet
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Prefix: %{_prefix}
BuildArch: x86_64
Vendor: Centre for Comparative Genomics <yabi@ccg.murdoch.edu.au>
BuildRequires: python%{pyver}-virtualenv python%{pyver}-devel postgresql94-devel libxml2-devel libxslt-devel openldap-devel
Requires: python%{pyver} openssl httpd python%{pyver}-mod_wsgi postgresql94-libs libxml2
Requires(pre): shadow-utils, /usr/sbin/useradd, /usr/bin/getent
Requires(postun): /usr/sbin/userdel

%description 
Test.

%package admin
Summary: yabi Django web application
Group: Applications/Internet

%description admin
Django web application implementing the web front end for Yabi.

%package shell
Summary: yabi shell
Group: Applications/Internet

%description shell
Yabi command line shell

%prep

if [ -d ${RPM_BUILD_ROOT}%{installdir} ]; then
    echo "Cleaning out stale build directory" 1>&2
    rm -rf ${RPM_BUILD_ROOT}%{installdir}
fi

# Turn off brp-python-bytecompile because it compiles the settings file.
%global __os_install_post %(echo '%{__os_install_post}' | sed -e 's!/usr/lib[^[:space:]]*/brp-python-bytecompile[[:space:]].*$!!g')

%install

for directory in "%{staticdir} %{logdir} %{storedir} %{scratchdir} %{mediadir}"; do
    mkdir -p $directory;
done;

if ! test -e $CCGSOURCEDIR/build-number-.txt; then
    echo '#Generated by spec file' > build-number.txt
    export TZ=Australia/Perth
    DATE=`date`
    echo "build.timestamp=\"$DATE\"" >> build-number.txt
fi
echo "build.user=\"$USER\"" >> build-number.txt
echo "build.host=\"$HOSTNAME\"" >> build-number.txt
cp build-number.txt %{buildinstalldir}/

##############################
# yabi-admin

cd $CCGSOURCEDIR/yabi

# Create a python prefix with app requirements
mkdir -p %{buildinstalldir}
virtualenv-%{pybasever} %{buildinstalldir}
. %{buildinstalldir}/bin/activate

# Use specific version of pip -- avoids surprises with deprecated
# options, etc.
pip install --force-reinstall --upgrade 'pip>=7.0,<8.0'
pip --version

export PATH=$PATH:/usr/pgsql-9.4/bin

# Install package into the prefix
# TODO - temporarily added --no-use-wheel below, because of jmespath package has a wrong wheel
# See https://github.com/jmespath/jmespath.py/issues/90
pip install --no-use-wheel -r runtime-requirements.txt
pip install .

# Fix up paths in virtualenv, enable use of global site-packages
virtualenv-%{pybasever} --relocatable %{buildinstalldir}
find %{buildinstalldir} -name \*py[co] -exec rm {} \;
find %{buildinstalldir} -name no-global-site-packages.txt -exec rm {} \;
sed -i "s|`readlink -f ${RPM_BUILD_ROOT}`||g" %{buildinstalldir}/bin/*

# Strip out mention of rpm buildroot from the pip install record
find %{buildinstalldir} -name RECORD -exec sed -i -e "s|${RPM_BUILD_ROOT}||" {} \;

# Strip debug syms out of the compiled python modules which are in the
# build root.
find %{buildinstalldir} -name \*.so -exec strip -g {} \;

# don't need a copy of python interpreter in the virtualenv
rm %{buildinstalldir}/bin/python*

# Create symlinks under install directory to real persistent data directories
APP_SETTINGS_FILE=`find %{buildinstalldir} -path "*/%{webappname}/settings.py" | sed s:^%{buildinstalldir}/::`
APP_PACKAGE_DIR=`dirname ${APP_SETTINGS_FILE}`
VENV_LIB_DIR=`dirname ${APP_PACKAGE_DIR}`

# Create static files symlink within module directory
ln -fsT %{installdir}/static %{buildinstalldir}/${VENV_LIB_DIR}/static

# Create symlinks under install directory to real persistent data directories
ln -fsT /var/log/%{webappname} %{buildinstalldir}/${VENV_LIB_DIR}/log
ln -fsT /var/lib/%{webappname}/scratch %{buildinstalldir}/${VENV_LIB_DIR}/scratch
ln -fsT /var/lib/%{webappname}/store %{buildinstalldir}/${VENV_LIB_DIR}/store
ln -fsT /var/lib/%{webappname}/media %{buildinstalldir}/${VENV_LIB_DIR}/media

# Install WSGI configuration into httpd/conf.d
install -D ../centos/%{webappname}.ccg %{buildroot}/etc/httpd/conf.d/%{webappname}.ccg
install -D ../centos/django.wsgi %{buildinstalldir}/django.wsgi

# Symlink django admin script
mkdir -p %{buildroot}/%{_bindir}
ln -fsT %{installdir}/bin/%{webappname}-manage.py %{buildroot}/%{_bindir}/%{webappname}

# Install yabi's celeryd init script system wide
install -m 0755 -D init_scripts/centos/celeryd.init %{buildroot}/etc/init.d/celeryd
install -m 0644 -D init_scripts/centos/celeryd.default %{buildroot}/etc/default/celeryd
# also install celery-flower
install -m 0755 -D init_scripts/centos/celery-flower.init %{buildroot}/etc/init.d/celery-flower

# make dirs for celery
mkdir -p %{buildroot}/var/log/celery
mkdir -p %{buildroot}/var/run/celery

# Install prodsettings conf file to /etc, and replace with symlink
install --mode=0640 -D ../centos/yabi.conf.example %{buildroot}/etc/yabi/yabi.conf
install --mode=0640 -D yabi/prodsettings.py %{buildroot}/etc/yabi/settings.py
ln -sfT /etc/yabi/settings.py %{buildinstalldir}/${APP_PACKAGE_DIR}/prodsettings.py

##############################
# yabi-shell

cd $CCGSOURCEDIR/yabish

# Create a python prefix with app requirements
mkdir -p %{shbuildinstalldir}
virtualenv-%{pybasever} %{shbuildinstalldir}
. %{shbuildinstalldir}/bin/activate

# Use specific version of pip -- avoids surprises with deprecated
# options, etc.
pip install --force-reinstall --upgrade 'pip==8.1.2'

# Install package into the prefix
pip install -r requirements.txt
pip install .

# Fix up paths in virtualenv, enable use of global site-packages
virtualenv-%{pybasever} --relocatable %{shbuildinstalldir}
find %{shbuildinstalldir} -name \*py[co] -exec rm {} \;
find %{shbuildinstalldir} -name no-global-site-packages.txt -exec rm {} \;
sed -i "s|`readlink -f ${RPM_BUILD_ROOT}`||g" %{shbuildinstalldir}/bin/*

# Strip out mention of rpm buildroot from the pip install record
find %{shbuildinstalldir} -name RECORD -exec sed -i -e "s|${RPM_BUILD_ROOT}||" {} \;

# don't need a copy of python interpreter in the virtualenv
rm %{shbuildinstalldir}/bin/python*

# Symlink script into system bin
mkdir -p %{buildroot}/%{_bindir}
ln -fsT %{shinstalldir}/bin/yabish %{buildroot}/%{_bindir}/yabish

%pre admin
# https://fedoraproject.org/wiki/Packaging:UsersAndGroups?rd=Packaging/UsersAndGroups
/usr/bin/getent group celery >/dev/null || /usr/sbin/groupadd -r celery
/usr/bin/getent passwd celery >/dev/null || \
    /usr/sbin/useradd -r -g celery -d /var/run/celery -s /bin/bash \
    -c "celery distributed task queue" celery
/usr/sbin/usermod -a -G apache celery
exit 0

%post admin
rm -rf %{installdir}/static/*
yabi collectstatic --noinput > /dev/null
# Remove root-owned logged files just created by collectstatic
rm -rf /var/log/%{webappname}/*
# Touch the wsgi file to get the app reloaded by mod_wsgi
touch %{installdir}/django.wsgi

%preun admin
if [ "$1" = "0" ]; then
    # Nuke staticfiles if not upgrading
    rm -rf %{installdir}/static/*
fi

%postun admin
if [ "$1" = "0" ]; then
    # clean up celery user, unless the uninstall is due to an upgrade
    /usr/sbin/userdel celery
fi

%files admin
%defattr(-,apache,apache,-)
/etc/httpd/conf.d/*
%{_bindir}/%{webappname}
%attr(-,apache,,apache) %{webapps}/%{webappname}
%attr(-,apache,,apache) /var/log/%{webappname}
%attr(-,apache,,apache) /var/lib/%{webappname}
%attr(-,celery,,celery) /var/run/celery
%attr(-,celery,,celery) /var/log/celery
%attr(-,root,,root) /etc/init.d/celeryd
%attr(-,root,,root) /etc/default/celeryd
%attr(-,root,,root) /etc/init.d/celery-flower
%attr(710,root,apache) /etc/yabi
%attr(640,root,apache) /etc/yabi/settings.py
%attr(640,root,apache) /etc/yabi/yabi.conf
%config(noreplace) /etc/yabi/settings.py
%config(noreplace) /etc/yabi/yabi.conf

%files shell
%defattr(-,root,root,-)
%{_bindir}/yabish
%{shinstalldir}
