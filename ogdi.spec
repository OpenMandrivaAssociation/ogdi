# TODO: separate gltpd to -server package, add init script (requires portmap)

%define name	ogdi
%define libname %mklibname %{name}
%define libminor	31

Summary:	Open Geographic Datastore Interface
Name:		%{name}
Version:	3.1.5
Release:	%mkrel 6
License:	BSD
Group:		Sciences/Geosciences
URL:		http://ogdi.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}.tar.bz2
Source1:	http://ogdi.sourceforge.net/ogdi.pdf
Patch0:		%{name}-driversdir.patch
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

%package -n %{libname}-devel
Summary:	OGDI header files and documentation
Group:		Sciences/Geosciences
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
#Manually provide these until library issues are resolved:
Provides:	devel(libexpat_ogdi%{libminor}) 
Provides:	devel(libogdi%{libminor})
Provides:	devel(libzlib_ogdi%{libminor})

%description -n %{libname}-devel
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

%setup -q
%patch0 -p1

cp -f %{SOURCE1} .

%build
export CFLAGS="%optflags -DDONT_TD_VOID -fPIC -DPIC"
TOPDIR=`pwd`; TARGET=linux; export TOPDIR TARGET
LD_LIBRARY_PATH=$TOPDIR/bin/$TARGET;export LD_LIBRARY_PATH
%configure \
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
rm -rf $RPM_BUILD_ROOT

TOPDIR=`pwd`; TARGET=linux; export TOPDIR TARGET

%make install \
	INST_INCLUDE=$RPM_BUILD_ROOT%{_includedir} \
	INST_LIB=$RPM_BUILD_ROOT%{_libdir}/ogdi \
	INST_BIN=$RPM_BUILD_ROOT%{_bindir}

%make install -C ogdi/tcl_interface \
	INST_LIB=$RPM_BUILD_ROOT%{_libdir}/ogdi
%make install -C contrib/gdal \
	INST_LIB=$RPM_BUILD_ROOT%{_libdir}/ogdi
%make install -C ogdi/attr_driver/odbc \
	INST_LIB=$RPM_BUILD_ROOT%{_libdir}/ogdi

# only lib*ogdi* is common library, the rest are dlopened drivers
mv -f $RPM_BUILD_ROOT%{_libdir}/ogdi/*ogdi*.so $RPM_BUILD_ROOT%{_libdir}

%clean
rm -rf $RPM_BUILD_ROOT

%if %mdkversion < 200900
%post	-p /sbin/ldconfig -n %{libname}
%endif

%if %mdkversion < 200900
%postun	-p /sbin/ldconfig -n %{libname}
%endif

%files
%defattr(644,root,root,755)
%doc LICENSE NEWS
%attr(755,root,root) %{_bindir}/gltpd
%attr(755,root,root) %{_bindir}/ogdi_*
%dir %{_libdir}/ogdi
%attr(755,root,root) %{_libdir}/ogdi/lib[^le]*.so
%exclude %{_bindir}/example?

%files -n %{libname}
%defattr(-,root,root)
%attr(755,root,root) %{_libdir}/lib%{name}%{libminor}.so
#%attr(755,root,root) %{_libdir}/*_%{name}%{libminor}.so

%files -n %{libname}-devel
%defattr(644,root,root,755)
%doc ogdi.pdf
%{_includedir}/*.h
%attr(755,root,root) %{_libdir}/lib%{name}.so

%files odbc
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ogdi/liblodbc.so

%files -n tcl-ogdi
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/ogdi/libecs_tcl.so

