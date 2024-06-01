%define _disable_lto 1

%global pre_release %{nil}
%define pkgname mozjs
%define api 91
%define major 91
%define majorlib 0
%define libmozjs %mklibname %{pkgname} %{api} %{major}
%define libmozjs_devel %mklibname %{pkgname} %{api} -d

# (tpg) optimize a bit
%global optflags %{optflags} -O3

# Big endian platforms
%ifarch ppc ppc64 s390 s390x
%global big_endian 1
%endif

Summary:	JavaScript interpreter and libraries
Name:		mozjs91
Version:	91.13.0
Release:	4
License:	MPLv2.0 and BSD and GPLv2+ and GPLv3+ and LGPLv2.1 and LGPLv2.1+
URL:		https://developer.mozilla.org/en-US/docs/Mozilla/Projects/SpiderMonkey/Releases/%{major}
Source0:        https://ftp.mozilla.org/pub/firefox/releases/%{version}esr/source/firefox-%{version}esr.source.tar.xz

# Patches from Debian mozjs60, rebased for mozjs68:
Patch01:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/fix-soname.patch
Patch02:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/copy-headers.patch
Patch03:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/tests-increase-timeout.patch
Patch09:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/icu_sources_data.py-Decouple-from-Mozilla-build-system.patch
Patch10:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/icu_sources_data-Write-command-output-to-our-stderr.patch

Patch11:        https://src.fedoraproject.org/rpms/mozjs91/blob/rawhide/f/remove-sloppy-m4-detection-from-bundled-autoconf.patch
 
# Build fixes - https://hg.mozilla.org/mozilla-central/rev/ca36a6c4f8a4a0ddaa033fdbe20836d87bbfb873
Patch12:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/emitter.patch
 
# Build fixes
Patch14:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/init_patch.patch
# TODO: Check with mozilla for cause of these fails and re-enable spidermonkey compile time checks if needed
Patch15:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/spidermonkey_checks_disable.patch
 
# armv7 fixes
Patch16:	https://src.fedoraproject.org/rpms/mozjs68/raw/master/f/rust_armv7.patch
Patch17:	https://src.fedoraproject.org/rpms/mozjs78/raw/master/f/armv7_disable_WASM_EMULATE_ARM_UNALIGNED_FP_ACCESS.patch
 
# Patches from Fedora firefox package:
Patch26:	https://src.fedoraproject.org/rpms/mozjs68/raw/master/f/build-icu-big-endian.patch
 
# Support Python 3 in js tests
#Patch30:	https://src.fedoraproject.org/rpms/mozjs68/raw/master/f/jstests_python-3.patch

# aarch64 fixes for -O2
Patch40:	Save-x28-before-clobbering-it-in-the-regex-compiler.patch
Patch41:	Save-and-restore-non-volatile-x28-on-ARM64-for-generated-unboxed-object-constructor.patch

#Patch50:	firefox-60.2.2-add-riscv64.patch
#Patch51:	mozjs-52.8.1-fix-crash-on-startup.patch
Patch52:	mozjs-68-compile.patch

BuildRequires:	pkgconfig(icu-i18n)
BuildRequires:	pkgconfig(nspr)
BuildRequires:	pkgconfig(libffi)
BuildRequires:	pkgconfig(zlib)
BuildRequires:	pkgconfig(python2)
BuildRequires:	readline-devel
BuildRequires:	zip
BuildRequires:	python
BuildRequires:	rust
BuildRequires:	cargo
BuildRequires:	llvm-devel clang-devel

%description
JavaScript is the Netscape-developed object scripting language used in millions
of web pages and server applications worldwide. Netscape's JavaScript is a
super set of the ECMA-262 Edition 3 (ECMAScript) standard scripting language,
with only mild differences from the published standard.

%package -n %{libmozjs}
Provides:	mozjs%{major} = %{EVRD}
Summary:	JavaScript engine library

%description -n %{libmozjs}
JavaScript is the Netscape-developed object scripting language used in millions
of web pages and server applications worldwide. Netscape's JavaScript is a
super set of the ECMA-262 Edition 3 (ECMAScript) standard scripting language,
with only mild differences from the published standard.

%package -n %{libmozjs_devel}
Summary:	Header files, libraries and development documentation for %{name}
Provides:	mozjs%{major}-devel = %{EVRD}
Requires:	%{libmozjs} = %{EVRD}

%description -n %{libmozjs_devel}
This package contains the header files, static libraries and development
documentation for %{name}. If you like to develop programs using %{name},
you will need to install %{name}-devel.

%prep
%setup -q -n firefox-%{version}/js/src

pushd ../..
%config_update

%patch01 -p1 -b .01~
%patch02 -p1 -b .02~
%patch03 -p1 -b .03~
%patch09 -p1 -b .09~
%patch10 -p1 -b .10~
%patch11 -p1 -b .11~ 
%patch12 -p1 -b .12~
%patch14 -p1 -b .14~
%patch15 -p1 -b .15~
 
%ifarch %{arm}
# Correct armv7hl rust triple seems to be armv7-unknown-linux-gnueabihf and not armv7-unknown-linux-gnueabi
%patch16 -p1 -b .16~
# Disable WASM_EMULATE_ARM_UNALIGNED_FP_ACCESS as it causes the compilation to fail
# https://bugzilla.mozilla.org/show_bug.cgi?id=1526653
%patch17 -p1 -b .17~
%endif
 
# Patch for big endian platforms only
%if 0%{?big_endian}
%patch26 -p1 -b .26~
%endif
 
# Execute tests with Python 3
#patch30 -p1 -b .30~

#patch50 -p1 -b .50~
#%patch51 -p1 -b .51~
%patch52 -p1 -b .52~
popd

# Remove zlib directory (to be sure using system version)
rm -rf ../../modules/zlib

rm -rf ../../nsprpub
#cd ../../config/external/
#for i in freetype2 icu nspr nss sqlite zlib; do
#	rm -rf $i
#	mkdir $i
#	touch $i/moz.build
#done
#cd ../../js/src

# Use bundled autoconf
export M4=m4
export AWK=awk
export AC_MACRODIR=$(pwd)/../../build/autoconf/
 
pwd
sh ../../build/autoconf/autoconf.sh --localdir=$(pwd) configure.in > configure
chmod +x configure

# Don't use stuff removed in python 3.11
find ../../python -name "*.py" |xargs sed -i -e 's,"rU", "r",g'

# We trust our toolchain. More than we trust hardcodes copied from
# whatever someone found on a prehistoric brokenbuntu box.
for i in ../../security/sandbox/chromium/sandbox/linux/system_headers/*_linux_syscalls.h; do
    echo '#include <asm/unistd.h>' >$i
done


%build
%set_build_flags

export RUSTFLAGS="-C embed-bitcode"
export CARGO_PROFILE_RELEASE_LTO=true
export CFLAGS="%{optflags}"
export CXXFLAGS="$CFLAGS"
export LDFLAGS="%{build_ldflags}"

%ifarch %{arm} %{armx}
export CFLAGS="$CFLAGS -fPIC"
export CXXFLAGS="$CXXFLAGS -fPIC"
export LDFLAGS="$LDFLAGS -fPIC"
%endif

%configure \
  --with-system-icu \
  --with-system-zlib \
  --disable-tests \
  --disable-strip \
  --with-intl-api \
  --enable-readline \
  --enable-shared-js \
  --enable-optimize="-O3" \
  --enable-pie \
  --disable-jemalloc

%if 0%{?big_endian}
echo "Generate big endian version of config/external/icu/data/icud58l.dat"
cd ../..
  ./mach python intl/icu_sources_data.py .
  ls -l config/external/icu/data
  rm -f config/external/icu/data/icudt*l.dat
cd -
%endif

%make_build

%install
%make_install

# Fix permissions
chmod -x %{buildroot}%{_libdir}/pkgconfig/*.pc

# Remove unneeded files
rm %{buildroot}%{_bindir}/js%{major}-config
rm %{buildroot}%{_libdir}/libjs_static.ajs

# Rename library and create symlinks, following fix-soname.patch
mv %{buildroot}%{_libdir}/libmozjs-%{major}.so \
   %{buildroot}%{_libdir}/libmozjs-%{major}.so.0.0.0
ln -s libmozjs-%{major}.so.0.0.0 %{buildroot}%{_libdir}/libmozjs-%{major}.so.0
ln -s libmozjs-%{major}.so.0 %{buildroot}%{_libdir}/libmozjs-%{major}.so

%check
# Some tests will fail
tests/jstests.py -d -s --no-progress ../../js/src/js/src/shell/js || :

%files
%{_bindir}/js%{major}

%files -n %{libmozjs}
%{_libdir}/libmozjs-%{major}.so.%{majorlib}*

%files -n %{libmozjs_devel}
%{_libdir}/libmozjs-%{major}.so
%{_libdir}/pkgconfig/*.pc
%{_includedir}/mozjs-%{major}
