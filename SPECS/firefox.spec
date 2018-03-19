%define system_nss              1
%global nspr_version            4.13.1
%global nss_version             3.28.4-11
%define system_sqlite           0
%define sqlite_version          3.8.4.2
%define system_ffi              1
%define ffi_version             3.0.9
%define use_bundled_yasm        1
%define use_bundled_python      0
%define python_version          2.7.8
%define use_bundled_gcc         0
%define gcc_version             4.8.2-16
%define cairo_version           1.10.2
%define freetype_version        2.1.9
%define system_jpeg             1
%define system_libatomic        0
%define with_intl_api           1
%define use_baselinejit         1
%define official_branding       1
%define use_gtk3                0


%define debug_build             0
# This is for local builds or builds in mock with --no-clean
# It skips building of gcc, binutils and yasm rpms when they exists, it just installs
# them and doesn't delete them to allow recycling them in next build.
# SHOULD ALWAYS BE 0 WHEN BUILDING IN BREW
%define do_not_clean_rpms       0

# Configure and override build options for various platforms and RHEL versions
# ============================================================================

# RHEL7
%if 0%{?rhel} == 7
%ifarch s390x
%define use_bundled_gcc         1
%endif
%endif

# RHEL6
%if 0%{?rhel} == 6
%define use_bundled_python      1
%define use_bundled_gcc         1
%define use_bundled_yasm        1
%define system_ffi              0
%define use_bundled_binutils    1
%endif

# Require libatomic for ppc
%ifarch ppc
%define system_libatomic        1
%endif
# Big endian platforms
%ifarch ppc ppc64 s390 s390x
# Javascript Intl API is not supported on big endian platforms right now:
# https://bugzilla.mozilla.org/show_bug.cgi?id=1322212
%define with_intl_api           1
%define big_endian              1
%endif

# ============================================================================

# Avoid patch failures
%define _default_patch_fuzz 2


%define default_bookmarks_file  %{_datadir}/bookmarks/default-bookmarks.html
%define firefox_app_id          \{ec8030f7-c20a-464f-9b0e-13a3a9e97384\}
%define mozappdir               %{_libdir}/%{name}
%define build_langpacks         1
%define langpackdir             %{mozappdir}/langpacks
%if %{?system_sqlite}
# The actual sqlite version (see #480989):
%global sqlite_build_version %(pkg-config --silence-errors --modversion sqlite3 2>/dev/null || echo 65536)
%endif

Summary:        Mozilla Firefox Web browser
Name:           firefox
Version:        52.7.2
Release:        1%{?dist}
URL:            http://www.mozilla.org/projects/firefox/
License:        MPLv1.1 or GPLv2+ or LGPLv2+
Group:          Applications/Internet

%define         ext_version             esr
%define         tarballdir              firefox-%{version}%{?ext_version}

# From ftp://archive.mozilla.org/pub/firefox/releases/%{version}%{?ext_version}/source
Source0:        firefox-%{version}%{?ext_version}.source.tar.xz
%if %{build_langpacks}
Source1:        firefox-langpacks-%{version}%{?ext_version}-20180316.tar.xz
%endif
Source10:       firefox-mozconfig
Source12:       firefox-redhat-default-prefs.js
Source20:       firefox.desktop
Source600:      firefox.sh.in.rhel6
Source700:      firefox.sh.in.rhel7
Source23:       firefox.1
Source24:       mozilla-api-key
Source100:      find-external-requires
Source200:      https://www.python.org/ftp/python/2.7.8/Python-2.7.8.tgz
Source300:      gcc48-%{gcc_version}.el5.src.rpm
Source301:      yasm-1.2.0-3.el5.src.rpm
Source302:      devtoolset-2-binutils-2.23.52.0.1-10.el5.src.rpm

# Build patches
Patch0:         firefox-install-dir.patch
Patch5:         xulrunner-24.0-jemalloc-ppc.patch
Patch6:         webrtc-arch-cpu.patch
Patch8:         firefox-ppc64le.patch
#ALREADY Patch19:        mozilla-1319374-skia-endian.patch
Patch20:        build-s390-atomic.patch
Patch21:        build-icu-big-endian.patch
Patch22:        build-missing-getrandom.patch
Patch23:        build-nss-version.patch
Patch24:        build-nss-prbool.patch
Patch25:        build-s390-missing-include.patch

# RHEL patches
Patch101:       firefox-default.patch
# TODO code changed a lot, need to test it
Patch102:       firefox-enable-addons.patch
Patch103:       rhbz-966424.patch
Patch106:       firefox-enable-plugins.patch
Patch110:       mozilla-1170092-etc-conf.patch
Patch111:       rhbz-1173156.patch
Patch112:       mozilla-256180.patch
Patch114:       rhbz-1423012.patch
Patch116:       mozilla-1005640-accept-lang.patch

# Upstream patches
# Skia support for big endian platforms, since patch got review- I think we can delete that:
#Patch201:       mozilla-1005535.patch
# Kaie's patch, we'll most likely need this one
Patch202:       mozilla-1152515.patch
Patch203:       mozilla-1324096.patch

# RHEL7 patches

# RHEL6 patches
# HOPEFULY fixed Patch401:       build-el6-harfbuzz-old-glib.patch

# ---------------------------------------------------
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires:  desktop-file-utils
BuildRequires:  mesa-libGL-devel
BuildRequires:  zip
BuildRequires:  bzip2-devel
BuildRequires:  zlib-devel
BuildRequires:  libIDL-devel
%if %{?use_gtk3}
BuildRequires:  gtk3-devel
%else
BuildRequires:  gtk2-devel
%endif
BuildRequires:  gnome-vfs2-devel
BuildRequires:  libgnome-devel
BuildRequires:  libgnomeui-devel
BuildRequires:  krb5-devel
BuildRequires:  pango-devel
BuildRequires:  freetype-devel >= %{freetype_version}
BuildRequires:  libXt-devel
BuildRequires:  libXrender-devel
BuildRequires:  startup-notification-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  libnotify-devel
BuildRequires:  autoconf213
BuildRequires:  mesa-libGL-devel
BuildRequires:  autoconf213
BuildRequires:  xz
%if ! %{use_bundled_yasm}0
BuildRequires:  yasm
%endif
%if %{?system_sqlite}
BuildRequires:  sqlite-devel >= %{sqlite_version}
Requires:       sqlite >= %{sqlite_build_version}
%endif
%if %{?system_nss}
BuildRequires:  nspr-devel >= %{nspr_version}
BuildRequires:  nss-devel >= %{nss_version}
Requires:       nspr >= %{nspr_version}
Requires:       nss >= %{nss_version}
%endif
%if %{?system_sqlite}
BuildRequires:  sqlite-devel >= %{sqlite_version}
Requires:       sqlite >= %{sqlite_build_version}
%endif
%if %{?system_ffi}
BuildRequires:  libffi-devel >= %{ffi_version}
Requires:       libffi >= %{ffi_version}
%endif
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-devel
BuildRequires:  hunspell-devel
%if %{system_libatomic}
BuildRequires:  libatomic
Requires:       libatomic
%endif

# RHEL7 requires
%if 0%{?rhel} == 7
Requires:       redhat-indexhtml
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  system-bookmarks
Requires:       mozilla-filesystem
Requires:       liberation-fonts-common
Requires:       liberation-sans-fonts
BuildRequires:  dbus-glib-devel >= 0.60 
%endif

# RHEL6 requires
%if 0%{?rhel} == 6
BuildRequires:  desktop-file-utils
BuildRequires:  system-bookmarks
Requires:       system-bookmarks
Requires:       redhat-indexhtml
Requires:       mozilla-filesystem
Requires:       gtk2 >= 2.24
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  system-bookmarks
Requires:       mozilla-filesystem
Requires:       liberation-fonts-common
Requires:       liberation-sans-fonts
%endif

Obsoletes:      mozilla <= 37:1.7.13
Obsoletes:      firefox < 38.0
Conflicts:      firefox < 38.0
Provides:       webclient

%if %{use_bundled_python}
BuildRequires:  openssl-devel
%endif
# GCC 4.8 BuildRequires
# ==================================================================================
%if %{use_bundled_gcc}

%ifarch s390x
%global multilib_32_arch s390
%endif
%ifarch sparc64
%global multilib_32_arch sparcv9
%endif
%ifarch ppc64
%global multilib_32_arch ppc
%endif
%ifarch x86_64
%if 0%{?rhel} >= 6
%global multilib_32_arch i686
%else
%global multilib_32_arch i386
%endif
%endif

%global multilib_64_archs sparc64 ppc64 s390x x86_64

%if 0%{?rhel} >= 6
# Need binutils which support --build-id >= 2.17.50.0.17-3
# Need binutils which support %gnu_unique_object >= 2.19.51.0.14
# Need binutils which support .cfi_sections >= 2.19.51.0.14-33
BuildRequires: binutils >= 2.19.51.0.14-33
# While gcc doesn't include statically linked binaries, during testing
# -static is used several times.
BuildRequires: glibc-static
%else
# Don't have binutils which support --build-id >= 2.17.50.0.17-3
# Don't have binutils which support %gnu_unique_object >= 2.19.51.0.14
# Don't have binutils which  support .cfi_sections >= 2.19.51.0.14-33
BuildRequires: binutils >= 2.17.50.0.2-8
%endif
BuildRequires: zlib-devel, gettext, dejagnu, bison, flex, texinfo, sharutils
BuildRequires: /usr/bin/pod2man
%if 0%{?rhel} >= 7
BuildRequires: texinfo-tex
%endif
#BuildRequires: systemtap-sdt-devel >= 1.3
# For VTA guality testing
BuildRequires: gdb
# Make sure pthread.h doesn't contain __thread tokens
# Make sure glibc supports stack protector
# Make sure glibc supports DT_GNU_HASH
BuildRequires: glibc-devel >= 2.4.90-13
%if 0%{?rhel} >= 6
BuildRequires: elfutils-devel >= 0.147
BuildRequires: elfutils-libelf-devel >= 0.147
%else
BuildRequires: elfutils-devel >= 0.72
%endif
%ifarch ppc ppc64 s390 s390x sparc sparcv9 alpha
# Make sure glibc supports TFmode long double
BuildRequires: glibc >= 2.3.90-35
%endif
%ifarch %{multilib_64_archs} sparcv9 ppc
# Ensure glibc{,-devel} is installed for both multilib arches
BuildRequires: /lib/libc.so.6 /usr/lib/libc.so /lib64/libc.so.6 /usr/lib64/libc.so
%endif
%ifarch ia64
BuildRequires: libunwind >= 0.98
%endif
# Need .eh_frame ld optimizations
# Need proper visibility support
# Need -pie support
# Need --as-needed/--no-as-needed support
# On ppc64, need omit dot symbols support and --non-overlapping-opd
# Need binutils that owns /usr/bin/c++filt
# Need binutils that support .weakref
# Need binutils that supports --hash-style=gnu
# Need binutils that support mffgpr/mftgpr
#%if 0%{?rhel} >= 6
## Need binutils which support --build-id >= 2.17.50.0.17-3
## Need binutils which support %gnu_unique_object >= 2.19.51.0.14
## Need binutils which support .cfi_sections >= 2.19.51.0.14-33
#Requires: binutils >= 2.19.51.0.14-33
#%else
## Don't have binutils which support --build-id >= 2.17.50.0.17-3
## Don't have binutils which support %gnu_unique_object >= 2.19.51.0.14
## Don't have binutils which  support .cfi_sections >= 2.19.51.0.14-33
#Requires: binutils >= 2.17.50.0.2-8
#%endif
## Make sure gdb will understand DW_FORM_strp
#Conflicts: gdb < 5.1-2
#Requires: glibc-devel >= 2.2.90-12
#%ifarch ppc ppc64 s390 s390x sparc sparcv9 alpha
## Make sure glibc supports TFmode long double
#Requires: glibc >= 2.3.90-35
#%endif
#Requires: libgcc >= 4.1.2-43
#Requires: libgomp >= 4.4.4-13
#%if 0%{?rhel} == 6
#Requires: libstdc++ >= 4.4.4-13
#%else
#Requires: libstdc++ = 4.1.2
#%endif
##FIXME gcc version
#Requires: libstdc++-devel = %{version}-%{release}
BuildRequires: gmp-devel >= 4.1.2-8
%if 0%{?rhel} >= 6
BuildRequires: mpfr-devel >= 2.2.1
%endif
%if 0%{?rhel} >= 7
BuildRequires: libmpc-devel >= 0.8.1
%endif

%endif # bundled gcc BuildRequires
# ==================================================================================
# Override internal dependency generator to avoid showing libraries provided by this package
# in dependencies:
AutoProv: 0
%define _use_internal_dependency_generator 0
%define __find_requires %{SOURCE100}

%description
Mozilla Firefox is an open-source web browser, designed for standards
compliance, performance and portability.

#---------------------------------------------------------------------

%prep
%setup -q -c
cd %{tarballdir}

# Build patches
# We have to keep original patch backup extension to go thru configure without problems with tests
%patch0 -p1 -b .orig
%patch5 -p1 -b .jemalloc-ppc.patch
%patch6 -p1 -b .webrtc-arch-cpu
%patch8 -p2 -b .ppc64le
#ALREADY %patch19 -p1 -b .skia-endian
%patch20 -p1 -b .s390-atomic
%patch22 -p1 -b .missing-getrandom
%patch23 -p1 -b .nss-version
%patch24 -p1 -b .nss-prbool
%patch25 -p1 -b .s390-missing-include

# RPM specific patches
%patch101 -p1 -b .default
%patch102 -p1 -b .addons
%patch103 -p1 -b .rhbz-966424
%patch106 -p2 -b .plugins
%patch110 -p1 -b .moz-1170092-etc-conf
%patch111 -p2 -b .rhbz-1173156
%patch112 -p1 -b .mozbz-256180
%patch114 -p1 -b .rhbz-1423012
%patch116 -p1 -b .mozbz-1005640-accept-lang

# Upstream patches
#%patch201 -p1 -b .mozbz-1005535 see Patch201 comment
%patch202 -p1 -b .mozbz-1152515
%patch203 -p1 -b .mozbz-1324096

# RHEL7 only patches
%if %{?rhel} == 7
%endif

#%if %{?rhel} == 6
#HOPEFULY FIXED %patch401 -p1 -b .harfbuzz-old-glib
#%endif

# Patch for big endian platforms only
%if 0%{?big_endian}
%patch21 -p1 -b .s390-atomic
%endif

%{__rm} -f .mozconfig
%{__cp} %{SOURCE10} .mozconfig
%{__cp} %{SOURCE24} mozilla-api-key

function add_to_mozconfig() {
  mozconfig_entry=$1
  echo "ac_add_options --$1" >> .mozconfig
}

# Modify mozconfig file
%if %{official_branding}
 add_to_mozconfig "enable-official-branding"
%endif

%if %{?use_gtk3}
 add_to_mozconfig "enable-default-toolkit=cairo-gtk3"
%else
 add_to_mozconfig "enable-default-toolkit=cairo-gtk2"
%endif

%if %{?system_sqlite}
 add_to_mozconfig "enable-system-sqlite"
%else
 add_to_mozconfig "disable-system-sqlite"
%endif

%if %{?system_nss}
 add_to_mozconfig "with-system-nspr"
 add_to_mozconfig "with-system-nss"
%else
 add_to_mozconfig "without-system-nspr"
 add_to_mozconfig "without-system-nss"
%endif

# RHEL 7 mozconfig changes:
%if 0%{rhel} >= 6
 add_to_mozconfig "enable-startup-notification"
 add_to_mozconfig "enable-jemalloc"
%endif

# RHEL 6
%if 0%{rhel} == 6
 # Disable dbus, because we're unable to build with its support in brew
 add_to_mozconfig "disable-dbus"
 # ctypes require system libffi for these platforms and RHEL6 does not have libffi >= 3.0.9 available
 %ifarch ppc64 ppc64le ppc s390 s390x
  add_to_mozconfig "disable-ctypes"
 %endif
%endif

%ifarch aarch64 ppc64 ppc64le ppc s390 s390x
 add_to_mozconfig "disable-ion"
%endif

%ifarch aarch64 ppc ppc64 s390 s390x
 add_to_mozconfig "disable-skia"
%endif

# Debug build flags
%if %{?debug_build}
 add_to_mozconfig "enable-debug"
 add_to_mozconfig "disable-optimize"
%else
 add_to_mozconfig "disable-debug"
 add_to_mozconfig "enable-optimize"
%endif

%if %{?with_intl_api}
 add_to_mozconfig "with-intl-api"
%else
 add_to_mozconfig "without-intl-api"
%endif
#TODO reconsider this, really needed for RHEL7 or even RHEL6? Disabling this 
#also require to disable-fmp4 and most likely disable-eme
#Disabled due to rhbz#1330898
#add_to_mozconfig "disable-ffmpeg"

#TODO what's this?
#FIXME RTTI?? RHEL5/6
# ac_add_options --enable-cpp-rtti
# RHEL7: ac_add_options --with-system-bz2
# RHEL5: never been there, but is it usable --enable-gnomeui ????

%if %{use_bundled_python}
 # Prepare Python 2.7 sources
 tar xf %{SOURCE200}
%endif

#---------------------------------------------------------------------

%build

function build_bundled_package() {
  PACKAGE_RPM=$1
  PACKAGE_FILES=$2
  PACKAGE_SOURCE=$3
  PACKAGE_DIR="%{_topdir}/RPMS"

  PACKAGE_ALREADY_BUILD=0
  %if %{do_not_clean_rpms}
    if ls $PACKAGE_DIR/$PACKAGE_RPM; then
      PACKAGE_ALREADY_BUILD=1
    fi
    if ls $PACKAGE_DIR/%{_arch}/$PACKAGE_RPM; then
      PACKAGE_ALREADY_BUILD=1
    fi
  %endif
  if [ $PACKAGE_ALREADY_BUILD == 0 ]; then
    echo "Rebuilding $PACKAGE_RPM from $PACKAGE_SOURCE"; echo "==============================="
    rpmbuild --nodeps --rebuild $PACKAGE_SOURCE
  fi

  if [ ! -f $PACKAGE_DIR/$PACKAGE_RPM ]; then
    # Hack for tps tests
    ARCH_STR=%{_arch}
    %ifarch i386 i686
    ARCH_STR="i?86"
    %endif
    PACKAGE_DIR="$PACKAGE_DIR/$ARCH_STR"
  fi
  pushd $PACKAGE_DIR
  echo "Installing $PACKAGE_DIR/$PACKAGE_RPM"; echo "==============================="
  rpm2cpio $PACKAGE_DIR/$PACKAGE_RPM | cpio -iduv
  # Clean rpms to avoid including them to package
  %if ! %{do_not_clean_rpms}0
    rm -f $PACKAGE_FILES
  %endif

  PATH=$PACKAGE_DIR/usr/bin:$PATH
  export PATH
  LD_LIBRARY_PATH=$PACKAGE_DIR/usr/%{_lib}
  export LD_LIBRARY_PATH
  popd
}

# Build and install local yasm if needed
# ======================================
%if %{use_bundled_yasm}
  build_bundled_package 'yasm-1*.rpm' 'yasm-*.rpm' '%{SOURCE301}'
%endif

# Install local binutils if needed
# ======================================
%if 0%{?use_bundled_binutils}
  build_bundled_package 'binutils-2*.rpm' 'binutils*.rpm' '%{SOURCE302}'
%endif

# Install local GCC if needed
# ======================================
%if %{use_bundled_gcc}
  build_bundled_package 'gcc48-%{gcc_version}*.rpm' 'gcc48-*.rpm' '%{SOURCE300}'
  export CXX=g++
%endif


# Install local Python if needed
# ======================================
%if %{use_bundled_python}
    echo "Rebuilding Python"; echo "==============================="
  pushd %{tarballdir}

  # Build Python 2.7 and set environment
  BUILD_DIR=`pwd`/python_build
  cd Python-%{python_version}
  ./configure --prefix=$BUILD_DIR --exec-prefix=$BUILD_DIR
  make
  make install
  cd -

  PATH=$BUILD_DIR/bin:$PATH
  export PATH
  popd
%endif # bundled Python

%if %{?system_sqlite}
  # Do not proceed with build if the sqlite require would be broken:
  # make sure the minimum requirement is non-empty, ...
  sqlite_version=$(expr "%{sqlite_version}" : '\([0-9]*\.\)[0-9]*\.') || exit 1
  # ... and that major number of the computed build-time version matches:
  case "%{sqlite_build_version}" in
    "$sqlite_version"*) ;;
    *) exit 1 ;;
  esac
%endif

echo "Building Firefox"; echo "==============================="
cd %{tarballdir}

# Hack for missing shell when building in brew on RHEL6 and RHEL5
%if 0%{?rhel} <= 6
export SHELL=/bin/sh
%endif

echo "Generate big endian version of config/external/icu/data/icud58l.dat"
%if 0%{?big_endian}
  ./mach python intl/icu_sources_data.py .
  ls -l config/external/icu/data
  rm -f config/external/icu/data/icudt*l.dat
%endif


# 1. Mozilla builds with -Wall with exception of a few warnings which show up
#    everywhere in the code; so, don't override that.
# 2. -Werror=format-security causes build failures when -Wno-format is explicitly given
#    for some sources
MOZ_OPT_FLAGS=$(echo "$RPM_OPT_FLAGS -fpermissive -Wformat-security -Wformat -Werror=format-security" | %{__sed} -e 's/-Wall//')

# TODO check if necessery
%ifarch s390
MOZ_OPT_FLAGS=$(echo "$MOZ_OPT_FLAGS" | %{__sed} -e 's/-g/-g1/')
%endif

# Avoid failing builds because OOM killer on some arches
%ifarch s390 %{arm} ppc
MOZ_LINK_FLAGS="$MOZ_LINK_FLAGS -Wl,--no-keep-memory -Wl,--reduce-memory-overheads"
%endif

%if %{rhel} == 6
  %if %{system_libatomic}
    MOZ_LINK_FLAGS="$MOZ_LINK_FLAGS -l:libatomic.so.1"
  %endif
%endif

%if %{?debug_build}
  MOZ_OPT_FLAGS=$(echo "$MOZ_OPT_FLAGS" | %{__sed} -e 's/-O2//')
%endif

export CFLAGS=$(echo "$MOZ_OPT_FLAGS" | %{__sed} -e 's/-fpermissive//')
export CXXFLAGS=$MOZ_OPT_FLAGS
export LDFLAGS="-Wl,--verbose $MOZ_LINK_FLAGS"

export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

MOZ_SMP_FLAGS=-j1
[ -z "$RPM_BUILD_NCPUS" ] && \
     RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"
[ "$RPM_BUILD_NCPUS" -ge 2 ] && MOZ_SMP_FLAGS=-j2
[ "$RPM_BUILD_NCPUS" -ge 4 ] && MOZ_SMP_FLAGS=-j4
[ "$RPM_BUILD_NCPUS" -ge 8 ] && MOZ_SMP_FLAGS=-j8

MOZ_APP_DIR=%{_libdir}/%{name}

make -f client.mk build STRIP="/bin/true" MOZ_MAKE_FLAGS="$MOZ_SMP_FLAGS"

#---------------------------------------------------------------------

%install
# Hack for missing shell when building in brew on RHEL6 and RHEL5
%if 0%{?rhel} <= 6
export SHELL=/bin/sh
%endif

cd %{tarballdir}
%{__rm} -rf $RPM_BUILD_ROOT

# set up our default bookmarks
%{__cp} -p %{default_bookmarks_file} objdir/dist/bin/browser/defaults/profile/bookmarks.html

# Make sure locale works for langpacks
%{__cat} > objdir/dist/bin/browser/defaults/preferences/firefox-l10n.js << EOF
pref("general.useragent.locale", "chrome://global/locale/intl.properties");
EOF


DESTDIR=$RPM_BUILD_ROOT make -C objdir install

%{__mkdir_p} $RPM_BUILD_ROOT{%{_libdir},%{_bindir},%{_datadir}/applications}

desktop-file-install \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
  --add-category WebBrowser \
  --add-category Network \
  %{SOURCE20}

# Set up the firefox start script, unfortunatelly it is different for each RHEL
rm -rf $RPM_BUILD_ROOT%{_bindir}/firefox
FIREFOX_SH_SOURCE=%{SOURCE700}
%if %{rhel} == 6
  FIREFOX_SH_SOURCE=%{SOURCE600}
%endif
cp $FIREFOX_SH_SOURCE $RPM_BUILD_ROOT%{_bindir}/firefox
%{__chmod} 755 $RPM_BUILD_ROOT%{_bindir}/firefox

# Installing man page
%{__install} -p -D -m 644 %{SOURCE23} $RPM_BUILD_ROOT%{_mandir}/man1/firefox.1

%{__rm} -f $RPM_BUILD_ROOT/%{mozappdir}/firefox-config

for s in 16 22 24 32 48 256; do
    %{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${s}x${s}/apps
    %{__cp} -p browser/branding/official/default${s}.png \
               $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${s}x${s}/apps/firefox.png
done

echo > ../%{name}.lang
%if %{build_langpacks}
# Extract langpacks, make any mods needed, repack the langpack, and install it.
%{__mkdir_p} $RPM_BUILD_ROOT%{langpackdir}
%{__xz} -dc %{SOURCE1} | %{__tar} xf -
for langpack in `ls firefox-langpacks/*.xpi`; do
  language=`basename $langpack .xpi`
  extensionID=langpack-$language@firefox.mozilla.org
  %{__mkdir_p} $extensionID
  unzip $langpack -d $extensionID
  find $extensionID -type f | xargs chmod 644

  cd $extensionID
  zip -r9mX ../${extensionID}.xpi *
  cd -

  %{__install} -m 644 ${extensionID}.xpi $RPM_BUILD_ROOT%{langpackdir}
  language=`echo $language | sed -e 's/-/_/g'`
  echo "%%lang($language) %{langpackdir}/${extensionID}.xpi" >> ../%{name}.lang
done
%{__rm} -rf firefox-langpacks

# Install langpack workaround (see #707100, #821169)
function create_default_langpack() {
  language_long=$1
  language_short=$2
  cd $RPM_BUILD_ROOT%{langpackdir}
  ln -s langpack-$language_long@firefox.mozilla.org.xpi langpack-$language_short@firefox.mozilla.org.xpi
  cd -
  echo "%%lang($language_short) %{langpackdir}/langpack-$language_short@firefox.mozilla.org.xpi" >> ../%{name}.lang
}

# Table of fallbacks for each language
# please file a bug at bugzilla.redhat.com if the assignment is incorrect
create_default_langpack "bn-IN" "bn"
create_default_langpack "es-AR" "es"
create_default_langpack "fy-NL" "fy"
create_default_langpack "ga-IE" "ga"
create_default_langpack "gu-IN" "gu"
create_default_langpack "hi-IN" "hi"
create_default_langpack "hy-AM" "hy"
create_default_langpack "nb-NO" "nb"
create_default_langpack "nn-NO" "nn"
create_default_langpack "pa-IN" "pa"
create_default_langpack "pt-PT" "pt"
create_default_langpack "sv-SE" "sv"
create_default_langpack "zh-TW" "zh"
%endif # build_langpacks

# Keep compatibility with the old preference location.
%{__mkdir_p} $RPM_BUILD_ROOT/%{mozappdir}/defaults/preferences
%{__mkdir_p} $RPM_BUILD_ROOT/%{mozappdir}/browser/defaults
ln -s %{mozappdir}/defaults/preferences $RPM_BUILD_ROOT/%{mozappdir}/browser/defaults/preferences

# Install default ones
%{__cp} %{SOURCE12} ${RPM_BUILD_ROOT}%{mozappdir}/defaults/preferences/all-redhat.js
# Modify preset preferences
%if %{use_baselinejit}
  echo 'pref("javascript.options.baselinejit",      true);'  >> ${RPM_BUILD_ROOT}%{mozappdir}/defaults/preferences/all-redhat.js
%else
  echo '/* Workaround for rhbz#1134876 */'                   >> ${RPM_BUILD_ROOT}%{mozappdir}/defaults/preferences/all-redhat.js
  echo 'pref("javascript.options.baselinejit",      false);' >> ${RPM_BUILD_ROOT}%{mozappdir}/defaults/preferences/all-redhat.js
%endif

# System config dir
%{__mkdir_p} $RPM_BUILD_ROOT/%{_sysconfdir}/%{name}/pref

# System extensions
%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/mozilla/extensions/%{firefox_app_id}
%{__mkdir_p} $RPM_BUILD_ROOT%{_libdir}/mozilla/extensions/%{firefox_app_id}

# Copy over the LICENSE
%{__install} -p -c -m 644 LICENSE $RPM_BUILD_ROOT/%{mozappdir}

# Use the system dictionaries for system hunspell
%{__rm} -rf ${RPM_BUILD_ROOT}%{mozappdir}/dictionaries
ln -s %{_datadir}/myspell ${RPM_BUILD_ROOT}%{mozappdir}/dictionaries

# Clean firefox-devel debuginfo
rm -rf %{_prefix}/lib/debug/lib/%{name}-devel-*
rm -rf %{_prefix}/lib/debug/lib64/%{name}-devel-*

#---------------------------------------------------------------------

%clean
%{__rm} -rf $RPM_BUILD_ROOT

#---------------------------------------------------------------------

%post
update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :
if [ -x %{_bindir}/gtk-update-icon-cache ]; then
  %{_bindir}/gtk-update-icon-cache --quiet %{_datadir}/icons/hicolor || :
fi

%postun
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi
update-desktop-database &> /dev/null || :

%preun
# is it a final removal?
if [ $1 -eq 0 ]; then
  %{__rm} -rf %{mozappdir}/components
  %{__rm} -rf %{mozappdir}/extensions
  %{__rm} -rf %{mozappdir}/plugins
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files -f %{name}.lang
%defattr(-,root,root,-)
%{_bindir}/firefox
%doc %{_mandir}/man1/*
%dir %{_sysconfdir}/%{name}/*
%dir %{_datadir}/mozilla/extensions/%{firefox_app_id}
%dir %{_libdir}/mozilla/extensions/%{firefox_app_id}
%{_datadir}/icons/hicolor/16x16/apps/firefox.png
%{_datadir}/icons/hicolor/48x48/apps/firefox.png
%{_datadir}/icons/hicolor/22x22/apps/firefox.png
%{_datadir}/icons/hicolor/24x24/apps/firefox.png
%{_datadir}/icons/hicolor/256x256/apps/firefox.png
%{_datadir}/icons/hicolor/32x32/apps/firefox.png
%{_datadir}/applications/%{name}.desktop
%dir %{mozappdir}
%doc %{mozappdir}/LICENSE
%{mozappdir}/browser/chrome
%{mozappdir}/browser/chrome.manifest
%{mozappdir}/browser/features/aushelper@mozilla.org.xpi
%{mozappdir}/browser/features/e10srollout@mozilla.org.xpi
%{mozappdir}/browser/features/firefox@getpocket.com.xpi
%{mozappdir}/browser/features/webcompat@mozilla.org.xpi
#gone %{mozappdir}/browser/features/disableSHA1rollout@mozilla.org.xpi
#gone %dir %{mozappdir}/browser/components
#gone %{mozappdir}/browser/components/*.so
#gone %{mozappdir}/browser/components/*.manifest
%attr(644, root, root) %{mozappdir}/browser/blocklist.xml
%dir %{mozappdir}/browser/extensions
%{mozappdir}/browser/extensions/{972ce4c6-7e08-4474-a285-3208198ce6fd}.xpi
# gone %{mozappdir}/browser/features/loop@mozilla.org.xpi
%dir %{mozappdir}/langpacks
%{mozappdir}/browser/icons
%{mozappdir}/browser/omni.ja
%{mozappdir}/firefox
%{mozappdir}/firefox-bin
%{mozappdir}/run-mozilla.sh
%{mozappdir}/application.ini
%{mozappdir}/defaults/preferences/*
%{mozappdir}/browser/defaults/preferences
%exclude %{mozappdir}/removed-files
# gone %{mozappdir}/webapprt-stub
# gone %dir %{mozappdir}/webapprt
# g %{mozappdir}/webapprt/omni.ja
# g %{mozappdir}/webapprt/webapprt.ini
%{mozappdir}/dictionaries
%{mozappdir}/*.so
%{mozappdir}/omni.ja
%{mozappdir}/platform.ini
%{mozappdir}/plugin-container
%{mozappdir}/dependentlibs.list
%{mozappdir}/chrome.manifest
%{mozappdir}/fonts/EmojiOneMozilla.ttf
%{mozappdir}/gmp-clearkey
%if %{?use_gtk3}
%{mozappdir}/gtk2/*.so
%endif
%if %{?with_intl_api}
%if 0%{?big_endian}
%{mozappdir}/icudt58b.dat
%else
%{mozappdir}/icudt58l.dat
%endif
%endif
%exclude %{mozappdir}/defaults/pref/channel-prefs.js
%if !%{?system_nss}
%{mozappdir}/*.chk
%endif
%exclude %{_datadir}/idl/*
%exclude %{_includedir}/*
%exclude %{_libdir}/%{name}-devel-*/*

#---------------------------------------------------------------------

%changelog
* Sun Mar 18 2018 CentOS Sources <bugs@centos.org> - 52.7.2-1.el7.centos
- Apply debranding changes

* Fri Mar 16 2018 Jan Horak <jhorak@redhat.com> - 52.7.2-1
- Update to 52.7.2 ESR

* Thu Mar  8 2018 Jan Horak <jhorak@redhat.com> - 52.7.0-1
- Update to 52.7.0 ESR

* Thu Jan 18 2018 Martin Stransky <stransky@redhat.com> - 52.6.1-2
- Update to 52.6.0 ESR

* Wed Nov 29 2017 Jan Horak <jhorak@redhat.com> - 52.5.1-1
- Update to 52.5.1 ESR

* Thu Nov  9 2017 Jan Horak <jhorak@redhat.com> - 52.5.0-1
- Update to 52.5.0 ESR

* Mon Sep 25 2017 Jan Horak <jhorak@redhat.com> - 52.4.0-1
- Update to 52.4.0 ESR

* Thu Aug  3 2017 Jan Horak <jhorak@redhat.com> - 52.3.0-3
- Update to 52.3.0 ESR (b2)
- Require correct nss version

* Tue Jun 13 2017 Jan Horak <jhorak@redhat.com> - 52.2.0-1
- Update to 52.2.0 ESR

* Wed May 24 2017 Jan Horak <jhorak@redhat.com> - 52.1.2-1
- Update to 52.1.2 ESR

* Wed May 24 2017 Jan Horak <jhorak@redhat.com> - 52.0-7
- Added fix for accept language (rhbz#1454322)

* Wed Mar 22 2017 Jan Horak <jhorak@redhat.com> - 52.0-6
- Removing patch required for older NSS from RHEL 7.3
- Added patch for rhbz#1414564

* Fri Mar 17 2017 Martin Stransky <stransky@redhat.com> - 52.0-5
- Added fix for mozbz#1348168/CVE-2017-5428

* Mon Mar  6 2017 Jan Horak <jhorak@redhat.com> - 52.0-4
- Update to 52.0 ESR (b4)

* Thu Mar 2 2017 Martin Stransky <stransky@redhat.com> - 52.0-3
- Added fix for rhbz#1423012 - ppc64 gfx crashes

* Wed Mar  1 2017 Jan Horak <jhorak@redhat.com> - 52.0-2
- Enable system nss

* Tue Feb 28 2017 Martin Stransky <stransky@redhat.com> - 52.0-1
- Update to 52.0ESR (B1)
- Build RHEL7 package for Gtk3

* Mon Feb 27 2017 Martin Stransky <stransky@redhat.com> - 52.0-0.13
- Added fix for rhbz#1414535

* Tue Feb 21 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.12
- Update to 52.0b8

* Tue Feb  7 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.11
- Readded addons patch

* Mon Feb  6 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.10
- Update to 52.0b3

* Tue Jan 31 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.9
- Update to 52.0b2

* Fri Jan 27 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.8
- Update to 52.0b1

* Thu Dec  8 2016 Jan Horak <jhorak@redhat.com> - 52.0-0.5
- Firefox Aurora 52 testing build

* Tue Nov  8 2016 Jan Horak <jhorak@redhat.com> - 45.5.0-1
- Update to 45.5.0 ESR

* Mon Oct 31 2016 Jan Horak <jhorak@redhat.com> - 45.4.0-3
- Added upcoming upstream patches mozbz#1018486

* Mon Sep 26 2016 Jan Horak <jhorak@redhat.com> - 45.4.0-2
- Added Laszlo Ersek patch for aarch64 crashes

* Wed Sep  7 2016 Jan Horak <jhorak@redhat.com> - 45.4.0-1
- Update to 45.4.0 ESR

* Wed Jul 27 2016 Jan Horak <jhorak@redhat.com> - 45.3.0-1
- Update to 45.3.0 ESR

* Mon Jul 11 2016 Martin Stransky <stransky@redhat.com> - 45.2.0-3
- Added fix for mozbz#256180

* Mon Jun 20 2016 Martin Stransky <stransky@redhat.com> - 45.2.0-2
- Added fix for mozbz#975832, rhbz#1343202

* Fri Jun  3 2016 Jan Horak <jhorak@redhat.com> - 45.2.0-1
- Update to 45.2.0 ESR

* Tue May 10 2016 Martin Stransky <stransky@redhat.com> - 45.1.1-2
- Added fix for mozbz#1270046 - new Samba auth response

* Wed May  4 2016 Jan Horak <jhorak@redhat.com> - 45.1.1-1
- Update to 45.1.1 ESR

* Tue May 3 2016 Martin Stransky <stransky@redhat.com> - 45.1.0-3
- Disabled ffmpeg (rhbz#1330898)

* Fri Apr 29 2016 Jan Horak <jhorak@redhat.com> - 45.1.0-1
- Fixed some regressions introduced by rebase

* Thu Apr 21 2016 Jan Horak <jhorak@redhat.com> - 45.1.0-1
- Update to 45.1.0 ESR

* Tue Apr 12 2016 Jan Horak <jhorak@redhat.com> - 45.0.2-1
- Update to 45.0.2 ESR

* Wed Apr  6 2016 Jan Horak <jhorak@redhat.com> - 45.0.1-1
- Update to 45.0.1 ESR

* Mon Apr  4 2016 Martin Stransky <stransky@redhat.com> - 45.0-5
- Fixed crashed after start (rhbz#1323744, rhbz#1323738)

* Mon Apr  4 2016 Jan Horak <jhorak@redhat.com> - 45.0-4
- Added system-level location for configuring Firefox (rhbz#1206239)

* Mon Mar  7 2016 Jan Horak <jhorak@redhat.com> - 45.0-3
- Update to 45.0 ESR

* Fri Dec 11 2015 Jan Horak <jhorak@redhat.com> - 38.5.0-3
- Update to 38.5.0 ESR

* Thu Oct 29 2015 Jan Horak <jhorak@redhat.com> - 38.4.0-1
- Update to 38.4.0 ESR

* Tue Sep 15 2015 Jan Horak <jhorak@redhat.com> - 38.3.0-2
- Update to 38.3.0 ESR

* Wed Aug 26 2015 Martin Stransky <stransky@redhat.com> - 38.2.1-1
- Update to 38.2.1 ESR

* Fri Aug  7 2015 Jan Horak <jhorak@redhat.com> - 38.2.0-4
- Update to 38.2.0 ESR

* Thu Aug  6 2015 Jan Horak <jhorak@redhat.com> - 38.1.1-1
- Update to 38.1.1 ESR

* Thu Jun 25 2015 Jan Horak <jhorak@redhat.com> - 38.1.0-1
- Update to 38.1.0 ESR

* Thu May 21 2015 Jan Horak <jhorak@redhat.com> - 38.0.1-2
- Fixed rhbz#1222807 by removing preun section

* Fri May 15 2015 Martin Stransky <stransky@redhat.com> - 38.0.1-1
- Update to 38.0.1 ESR

* Thu May 14 2015 Martin Stransky <stransky@redhat.com> - 38.0-4
- Fixed rhbz#1221286 - After update to Firefox 38 ESR
  all RH preferences are gone

* Thu May  7 2015 Martin Stransky <stransky@redhat.com> - 38.0-3
- Enabled system nss
- Removed unused patches

* Mon May  4 2015 Jan Horak - 38.0-2
- Update to 38.0 ESR

* Mon Apr 27 2015 Martin Stransky <stransky@redhat.com> - 38.0b8-0.11
- Update to 38.0 Beta 8

* Wed Apr 22 2015 Martin Stransky <stransky@redhat.com> - 38.0b6-0.10
- Added patch for mozbz#1152515

* Tue Apr 21 2015 Martin Stransky <stransky@redhat.com> - 38.0b6-0.9
- Update to 38.0 Beta 6

* Mon Apr 20 2015 Martin Stransky <stransky@redhat.com> - 38.0b5-0.8
- Update to 38.0 Beta 5

* Fri Apr 10 2015 Martin Stransky <stransky@redhat.com> - 38.0b3-0.7
- Update to 38.0 Beta 3

* Fri Apr 10 2015 Martin Stransky <stransky@redhat.com> - 38.0b1-0.6
- Added patch for mozbz#1152391

* Thu Apr  9 2015 Marcin Juszkiewicz <mjuszkiewicz@redhat.com> - 38.0b1-0.5
- Fix build on AArch64 (based on upstream skia changes)

* Tue Apr 7 2015 Martin Stransky <stransky@redhat.com> - 38.0b1-0.4
- Enabled debug build

* Wed Apr  1 2015 Jan Horak <jhorak@redhat.com> - 38.0b1-1
- Update to 38.0b1

* Wed Feb 18 2015 Martin Stransky <stransky@redhat.com> - 31.5.0-2
- Update to 31.5.0 ESR Build 2

* Tue Jan  6 2015 Jan Horak <jhorak@redhat.com> - 31.4.0-1
- Update to 31.4.0 ESR

* Mon Jan 5 2015 Martin Stransky <stransky@redhat.com> - 31.3.0-6
- Fixed Bug 1140385 - [HP HPS 7.1 bug] assertion
  "sys_page_size == 0" when starting firefox

* Fri Dec 19 2014 Martin Stransky <stransky@redhat.com> - 31.3.0-5
- Fixed problems with dictionary (mozbz#1097550)
- JS JIT fixes for ppc64le

* Sat Nov 29 2014 Martin Stransky <stransky@redhat.com> - 31.3.0-3
- Fixed geolocation key location

* Fri Nov 28 2014 Martin Stransky <stransky@redhat.com> - 31.3.0-2
- Disable exact rooting for JS

* Wed Nov 26 2014 Martin Stransky <stransky@redhat.com> - 31.3.0-1
- Update to 31.3.0 ESR Build 2
- Fix for geolocation API (rhbz#1063739)

* Thu Nov 6 2014 Martin Stransky <stransky@redhat.com> - 31.2.0-5
- Enabled gstreamer-1 support (rhbz#1161077)

* Mon Oct 27 2014 Yaakov Selkowitz <yselkowi@redhat.com> - 31.2.0-4
- Fix webRTC for aarch64, ppc64le (rhbz#1148622)

* Tue Oct  7 2014 Jan Horak <jhorak@redhat.com> - 31.2.0-3
- Update to 31.2.0 ESR
- Fix for mozbz#1042889

* Wed Oct 1 2014 Martin Stransky <stransky@redhat.com> - 31.1.0-7
- Enable WebM on all arches

* Thu Sep 11 2014 Martin Stransky <stransky@redhat.com> - 31.1.0-6
- Enable all NPAPI plugins by default to keep compatibility
  with the FF24 line

* Wed Sep 10 2014 Martin Stransky <stransky@redhat.com> - 31.1.0-5
- Added workaround for rhbz#1134876

* Mon Sep 8 2014 Martin Stransky <stransky@redhat.com> - 31.1.0-3
- Disable mozilla::pkix (mozbz#1063315)
- Enable image cache

* Mon Sep 8 2014 Martin Stransky <stransky@redhat.com> - 31.1.0-2
- A workaround for rhbz#1110291

* Thu Aug 28 2014 Martin Stransky <stransky@redhat.com> - 31.1.0-1
- Update to 31.1.0 ESR

* Tue Aug 5 2014 Martin Stransky <stransky@redhat.com> - 31.0-3
- Built with system libvpx/WebM

* Mon Aug 4 2014 Martin Stransky <stransky@redhat.com> - 31.0-2
- Built with system nss/nspr

* Mon Jul 28 2014 Martin Stransky <stransky@redhat.com> - 31.0-1
- Update to 31.0 ESR

* Wed Jun  4 2014 Jan Horak <jhorak@redhat.com> - 24.6.0-1
- Update to 24.6.0 ESR

* Wed Apr 23 2014 Martin Stransky <stransky@redhat.com> - 24.5.0-2
- Removed unused patches

* Tue Apr 22 2014 Martin Stransky <stransky@redhat.com> - 24.5.0-1
- Update to 24.5.0 ESR

* Tue Apr 15 2014 Martin Stransky <stransky@redhat.com> - 24.4.0-3
- Added a workaround for Bug 1054242 - RHEVM: Extremely high memory
  usage in Firefox 24 ESR on RHEL 6.5

* Wed Mar 26 2014 Martin Stransky <stransky@redhat.com> - 24.4.0-2
- fixed rhbz#1067343 - Broken languagepack configuration 
  after firefox update

* Tue Mar 18 2014 Jan Horak <jhorak@redhat.com> - 24.4.0-1
- Update to 24.4.0 ESR

* Thu Feb 27 2014 Martin Stransky <stransky@redhat.com> - 24.3.0-3
- fixed rhbz#1054832 - Firefox does not support Camellia cipher

* Mon Feb  3 2014 Jan Horak <jhorak@redhat.com> - 24.3.0-1
- Update to 24.3.0 ESR

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 24.2.0-3
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 24.2.0-2
- Mass rebuild 2013-12-27

* Mon Dec 9 2013 Martin Stransky <stransky@redhat.com> - 24.2.0-1
- Update to 24.2.0 ESR

* Mon Dec 2 2013 Martin Stransky <stransky@redhat.com> - 24.1.0-5
- Fixed mozbz#938730 - avoid mix of memory allocators (crashes)
  when using system sqlite

* Tue Nov 26 2013 Martin Stransky <stransky@redhat.com> - 24.1.0-4
- Fixed rhbz#1034541 - No translation being picked up 
  from langpacks for firefox

* Fri Nov 8 2013 Martin Stransky <stransky@redhat.com> - 24.1.0-3
- Conflicts with old, xulrunner based firefox

* Thu Nov 7 2013 Martin Stransky <stransky@redhat.com> - 24.1.0-2
- Ship dependentlibs.list (rhbz#1027782)
- Nss/nspr dependency update

* Wed Nov 6 2013 Martin Stransky <stransky@redhat.com> - 24.1.0-1
- Update to 24.1.0 ESR

* Wed Nov 6 2013 Martin Stransky <stransky@redhat.com> - 24.0-2
- Build as stand alone browser, without xulrunner

* Thu Oct 31 2013 Martin Stransky <stransky@redhat.com> - 24.0-1
- Update to 24.0 ESR

* Thu Sep 12 2013 Jan Horak <jhorak@redhat.com> - 17.0.9-1
- Update to 17.0.9 ESR

* Thu Aug 29 2013 Martin Stransky <stransky@redhat.com> - 17.0.8-2
- Desktop file update
- Spec file tweaks

* Thu Aug 1 2013 Martin Stransky <stransky@redhat.com> - 17.0.8-1
- Update to 17.0.8 ESR

* Wed Jul 31 2013 Jan Horak <jhorak@redhat.com> - 17.0.7-2
- Updated manual page

* Thu Jun 20 2013 Jan Horak <jhorak@redhat.com> - 17.0.7-1
- Update to 17.0.7 ESR

* Fri May 17 2013 Jan Horak <jhorak@redhat.com> - 17.0.6-1
- Update to 17.0.6 ESR

* Fri May 17 2013 Martin Stransky <stransky@redhat.com> - 17.0.5-3
- Removed mozilla prefix from desktop file (rhbz#826960)

* Thu Apr 18 2013 Martin Stransky <stransky@redhat.com> - 17.0.5-2
- Updated XulRunner SDK check

* Fri Mar 29 2013 Jan Horak <jhorak@redhat.com> - 17.0.5-1
- Update to 17.0.5 ESR

* Thu Mar 14 2013 Martin Stransky <stransky@redhat.com> - 17.0.4-2
- Fixed rhbz#837606 - firefox has no x-scheme-handler/http mime

* Wed Mar 13 2013 Martin Stransky <stransky@redhat.com> - 17.0.4-1
- Update to 17.0.4 ESR
- Added fix for mozbz#239254 - [Linux] Support disk cache on a local path

* Tue Jan 15 2013 Martin Stransky <stransky@redhat.com> - 17.0.2-3
- Added NM preferences

* Fri Jan 11 2013 Martin Stransky <stransky@redhat.com> - 17.0.2-2
- Updated preferences (NFS, nspluginwrapper)

* Thu Jan 10 2013 Jan Horak <jhorak@redhat.com> - 17.0.2-1
- Update to 17.0.2 ESR

* Thu Dec 20 2012 Jan Horak <jhorak@redhat.com> - 17.0.1-1
- Update to 17.0.1 ESR

* Mon Oct  8 2012 Jan Horak <jhorak@redhat.com> - 10.0.8-2
- Update to 10.0.8 ESR

* Sat Aug 25 2012 Jan Horak <jhorak@redhat.com> - 10.0.7-1
- Update to 10.0.7 ESR

* Mon Jul 16 2012 Martin Stransky <stransky@redhat.com> - 10.0.6-1
- Update to 10.0.6 ESR

* Mon Jun 25 2012 Martin Stransky <stransky@redhat.com> - 10.0.5-4
- Enabled WebM

* Mon Jun 25 2012 Martin Stransky <stransky@redhat.com> - 10.0.5-2
- Added fix for mozbz#703633, rhbz#818341

* Fri Jun 1 2012 Martin Stransky <stransky@redhat.com> - 10.0.5-1
- Update to 10.0.5 ESR

* Sun Apr 22 2012 Martin Stransky <stransky@redhat.com> - 10.0.4-1
- Update to 10.0.4 ESR

* Tue Mar 6 2012 Martin Stransky <stransky@redhat.com> - 10.0.3-1
- Update to 10.0.3 ESR

* Thu Feb  9 2012 Jan Horak <jhorak@redhat.com> - 10.0.1-1
- Update to 10.0.1 ESR

* Tue Feb 7 2012 Martin Stransky <stransky@redhat.com> - 10.0-3
- Update to 10.0 ESR

* Mon Jan 30 2012 Martin Stransky <stransky@redhat.com> - 10.0-1
- Update to 10.0

* Mon Sep 26 2011 Martin Stransky <stransky@redhat.com> - 7.0-5
- Update to 7.0

* Tue Sep 20 2011 Jan Horak <jhorak@redhat.com> - 7.0-4
- Update to 7.0 Beta 6

* Tue Sep 13 2011 Martin Stransky <stransky@redhat.com> - 7.0-2
- Update to 7.0 Beta 4

* Mon Jul 11 2011 Martin Stransky <stransky@redhat.com> - 5.0-1
- Update to 5.0

* Mon Jun 13 2011 Jan Horak <jhorak@redhat.com> - 3.6.18-1
- Fixed #698313 - "background-repeat" css property isn't rendered well
- Update to 3.6.18

* Mon Apr 18 2011 Jan Horak <jhorak@redhat.com> - 3.6.17-1
- Update to 3.6.17

* Tue Mar  8 2011 Jan Horak <jhorak@redhat.com> - 3.6.15-1
- Update to 3.6.15

* Mon Feb 21 2011 Jan Horak <jhorak@redhat.com> - 3.6.14-4
- Update to build3

* Tue Feb  8 2011 Jan Horak <jhorak@redhat.com> - 3.6.14-3
- Update to build2

* Wed Jan 26 2011 Jan Horak <jhorak@redhat.com> - 3.6.14-2
- Update to 3.6.14
