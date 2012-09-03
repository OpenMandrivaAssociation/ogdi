# TODO: separate gltpd to -server package, add init script (requires portmap)

%define name	ogdi
%define major	3
%define libname %mklibname %{name} %{major}
%define develname %mklibname -d %{name}

%define beta	beta2

Summary:	Open Geographic Datastore Interface
Name:		%{name}
Version:	3.2.0
Release:	%mkrel 0.%{beta}.2
License:	BSD
Group:		Sciences/Geosciences
URL:		http://ogdi.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}.%{beta}.tar.gz
Source1:	http://ogdi.sourceforge.net/ogdi.pdf
Patch0:		patch_for_proj48_redhat.patch
Patch1:		ogdi-3.2.0.beta2-fix-str-fmt.patch
BuildRequires:	expat-devel
BuildRequires:	proj-devel
BuildRequires:	tcl-devel
BuildRequires:	unixODBC-devel
BuildRequires:	zlib-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
OGDI is the Open Geographic Datastore Interface. OGDI is an
application programming interface (API) that uses a standardized
access methods to work in conjunction with GIS software packages (the
application) and various geospatial data products. OGDI uses a
client/server architecture to facilitate the dissemination of
geospatial data products over any TCP/IP network, and a
driver-oriented approach to facilitate access to several geospatial
data products/formats.

%package -n %{libname}
Summary:	Open Geographic Datastore Interface - library
License:	BSD style
Group:		Sciences/Geosciences

%description -n %{libname}
OGDI is the Open Geographic Datastore Interface. OGDI is an
application programming interface (API) that uses a standardized
access methods to work in conjunction with GIS software packages (the
application) and various geospatial data products. OGDI uses a
client/server architecture to facilitate the dissemination of
geospatial data products over any TCP/IP network, and a
driver-oriented approach to facilitate access to several geospatial
data products/formats.

This package contains just the library required by applications using the
Open Geographic Datastore Interface.

%package -n %{develname}
Summary:	OGDI header files and documentation
Group:		Sciences/Geosciences
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:	lib%{name}-devel = %{version}-%{release}
#Manually provide these until library issues are resolved:
Provides:	devel(libexpat_ogdi%{libminor}) 
Provides:	devel(libogdi%{libminor})
Provides:	devel(libzlib_ogdi%{libminor})

%description -n %{develname}
OGDI header files and developer's documentation.

%package odbc
Summary:	ODBC driver for OGDI
Group:		Sciences/Geosciences
Requires:	%{name} = %{version}-%{release}

%description odbc
ODBC driver for OGDI.

%package -n tcl-ogdi
Summary:	TCL wrapper for OGDI
Summary(pl):	Interfejs TCL do OGDI
Group:		Sciences/Geosciences
Requires:	%{name} = %{version}-%{release}

%description -n tcl-ogdi
TCL wrapper for OGDI.

%prep

%setup -q -n %{name}-%{version}.%{beta}
%patch0 -p1
%patch1 -p0

cp -f %{SOURCE1} .

%build

TOPDIR=`pwd`; TARGET=Linux; export TOPDIR TARGET
INST_LIB=%{_libdir}/;export INST_LIB
export CFG=debug # for -g 

# do not compile with ssp. it will trigger internal bugs (to_fix_upstream)
OPT_FLAGS=`echo $RPM_OPT_FLAGS|sed -e 's/-Wp,-D_FORTIFY_SOURCE=2//g'`
export CFLAGS="$OPT_FLAGS -fPIC -DPIC -DDONT_TD_VOID -DUSE_TERMIO" 

%configure2_5x \
	--with-binconfigs \
	--with-expat \
	--with-proj \
	--with-zlib

# use the generated .mak file ...
cp -af config/linux.mak{,.old}
cp -af config/{L,l}inux.mak

# make doesn't survive a parallell build, so stop that...
make

make -C ogdi/tcl_interface \
	TCL_LINKLIB="-ltcl"
	
make -C contrib/gdal 

make -C ogdi/attr_driver/odbc \
	ODBC_LINKLIB="-lodbc"

%install
rm -rf %{buildroot}

# export env 
TOPDIR=`pwd`; TARGET=Linux; export TOPDIR TARGET

%makeinstall \
	INST_INCLUDE=%{buildroot}%{_includedir}/%{name} \
	INST_LIB=%{buildroot}%{_libdir} \
	INST_BIN=%{buildroot}%{_bindir}

#plugin install
%makeinstall -C ogdi/tcl_interface \
	INST_LIB=%{buildroot}%{_libdir}
%makeinstall -C contrib/gdal \
	INST_LIB=%{buildroot}%{_libdir}
%makeinstall -C ogdi/attr_driver/odbc \
	INST_LIB=%{buildroot}%{_libdir}

# only lib*ogdi* is common library, the rest are dlopened drivers
#mv -f %{buildroot}%{_libdir}/ogdi/*ogdi*.so %{buildroot}%{_libdir}

# remove example binary
rm -rf %{buildroot}%{_bindir}/example?

# we have multilib ogdi-config
%if "%{_lib}" == "lib"
%define cpuarch 32
%else
%define cpuarch 64
%endif

# fix file(s) for multilib issue
touch -r ogdi-config.in ogdi-config

# install pkgconfig file and ogdi-config
mkdir -p %{buildroot}%{_libdir}/pkgconfig
install -p -m 644 ogdi.pc %{buildroot}%{_libdir}/pkgconfig/
install -p -m 755 ogdi-config %{buildroot}%{_bindir}/ogdi-config-%{cpuarch}
# ogdi-config wrapper for multiarch
cat > %{buildroot}%{_bindir}/%{name}-config <<EOF
#!/bin/bash

ARCH=\$(uname -m)
case \$ARCH in
x86_64 | ppc64 | ia64 | s390x | sparc64 | alpha | alphaev6 )
ogdi-config-64 \${*}
;;
*)
ogdi-config-32 \${*}
;;
esac
EOF
chmod 755 %{buildroot}%{_bindir}/%{name}-config
touch -r ogdi-config.in %{buildroot}%{_bindir}/%{name}-config 

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post	-p /sbin/ldconfig -n %{libname}
%endif

%if %mdkversion < 200900
%postun	-p /sbin/ldconfig -n %{libname}
%endif

%files
%defattr(-,root,root,-)
%doc LICENSE NEWS ChangeLog README
%{_bindir}/gltpd
%{_bindir}/ogdi_*
%dir %{_libdir}/ogdi
%exclude %{_libdir}/%{name}/liblodbc.so
%exclude %{_libdir}/%{name}/libecs_tcl.so
%{_libdir}/%{name}/lib*.so 

%files -n %{libname}
%defattr(-,root,root)
%{_libdir}/libogdi.so.%{major}*

%files -n %{develname}
%defattr(-,root,root,-)
%doc ogdi.pdf
%doc ogdi/examples/example1/example1.c
%doc ogdi/examples/example2/example2.c
%{_bindir}/%{name}-config
%{_bindir}/%{name}-config-%{cpuarch}
%{_libdir}/pkgconfig/%{name}.pc
%dir %{_includedir}/%{name}
%{_includedir}/%{name}/*.h
%{_libdir}/libogdi.so 
%files odbc

%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ogdi/liblodbc.so

%files -n tcl-ogdi
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ogdi/libecs_tcl.so

