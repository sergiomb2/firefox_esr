# Use system sqlite?
%define system_sqlite           0
%define system_ffi              1

# Use system nss/nspr?
%define system_nss              1

# Gstreamer 1.0 support
%define enable_gstreamer        1

# Use system cairo?
%define system_cairo            0

# Build as a debug package?
%define debug_build             0

# Do we build a final version?
%define official_branding       1

# Minimal required versions
%if %{?system_nss}
%global nspr_version 4.10.8-2
%global nss_version 3.19.1-7
%endif

%define cairo_version 1.10.2
%define freetype_version 2.1.9
%define ffi_version 3.0.9
%global libvpx_version 1.3.0
%define _default_patch_fuzz 2

# Bookmark variables
%define default_bookmarks_file  %{_datadir}/bookmarks/default-bookmarks.html
%define firefox_app_id          \{ec8030f7-c20a-464f-9b0e-13a3a9e97384\}

%define mozappdir               %{_libdir}/%{name}
%define langpackdir             %{mozappdir}/langpacks

%if %{?system_sqlite}
%define sqlite_version 3.8.4.2
# The actual sqlite version (see #480989):
%global sqlite_build_version %(pkg-config --silence-errors --modversion sqlite3 2>/dev/null || echo 65536)
%endif

%define official_branding       1
%define build_langpacks         1

%if %{official_branding}
%define tarballdir  mozilla-esr38
%define ext_version esr
%endif


Summary:        Mozilla Firefox Web browser
Name:           firefox
Version:        38.4.0
Release:        1%{?prever}%{?dist}
URL:            http://www.mozilla.org/projects/firefox/
License:        MPLv1.1 or GPLv2+ or LGPLv2+
Group:          Applications/Internet
# From ftp://ftp.mozilla.org/pub/firefox/releases/%{version}%{?pretag}/source
Source0:        firefox-%{version}%{?prever}%{?ext_version}.source.tar.bz2
%if %{build_langpacks}
Source1:        firefox-langpacks-%{version}%{?ext_version}-20151029.tar.bz2
%endif
Source10:       firefox-mozconfig
Source11:       firefox-mozconfig-branded
Source12:       firefox-centos-default-prefs.js
Source20:       firefox.desktop
Source21:       firefox.sh.in
Source23:       firefox.1
Source24:       mozilla-api-key
Source100:      find-external-requires

# Build patches
Patch0:         firefox-install-dir.patch
Patch5:         xulrunner-24.0-jemalloc-ppc.patch
Patch6:         webrtc-arch-cpu.patch
Patch7:         build-no-format.patch
Patch8:         firefox-ppc64le.patch
Patch9:         firefox-debug.patch
Patch10:        firefox-nss-3.19.1.patch
Patch11:        build-nspr-prbool.patch

# RPM specific patches
Patch101:        firefox-default.patch
Patch102:        firefox-enable-addons.patch
Patch103:        rhbz-966424.patch
Patch106:        firefox-enable-plugins.patch
Patch108:        rhbz-1014858.patch
# Fix Skia Neon stuff on AArch64
Patch109:        aarch64-fix-skia.patch


# Upstream patches
Patch200:       firefox-duckduckgo.patch
Patch201:       mozilla-1005535.patch
Patch202:       mozilla-1152515.patch
Patch203:       mozilla-1204147.patch

%if %{official_branding}
# Required by Mozilla Corporation

%else
# Not yet approved by Mozillla Corporation


%endif

# ---------------------------------------------------
BuildRoot:      %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)
BuildRequires:  desktop-file-utils

BuildRequires:  mesa-libGL-devel
BuildRequires:  system-bookmarks
Requires:       redhat-indexhtml

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
%if %{?system_cairo}
BuildRequires:  cairo-devel >= %{cairo_version}
%endif
%if %{?system_sqlite}
BuildRequires:  sqlite-devel >= %{sqlite_version}
Requires:       sqlite >= %{sqlite_build_version}
%endif
%if %{?system_ffi}
BuildRequires:  libffi-devel >= %{ffi_version}
Requires:       libffi >= %{ffi_version}
%endif
BuildRequires:  libvpx-devel >= %{libvpx_version}
Requires:       libvpx >= %{libvpx_version}
%if %{?enable_gstreamer}
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
%endif
BuildRequires:  hunspell-devel
BuildRequires:  libpng-devel
BuildRequires:  libjpeg-devel
BuildRequires:  zip
BuildRequires:  bzip2-devel
BuildRequires:  zlib-devel
BuildRequires:  libIDL-devel
BuildRequires:  gtk2-devel
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
BuildRequires:  pulseaudio-libs-devel

Requires:       mozilla-filesystem
Requires:       liberation-fonts-common
Requires:       liberation-sans-fonts

BuildRequires:  autoconf213
Obsoletes:      mozilla <= 37:1.7.13
Obsoletes:      firefox < 24.1.0
Conflicts:      firefox < 24.1.0
Provides:       webclient

%define _use_internal_dependency_generator 0
%define __find_requires %{SOURCE100}

%description
Mozilla Firefox is an open-source web browser, designed for standards
compliance, performance and portability.

#---------------------------------------------------------------------

%prep
%setup -q -c
cd %{tarballdir}

# test if they exists
# Build patches
# We have to keep original patch backup extension to go thru configure without problems with tests
%patch0 -p1 -b .orig
%patch5 -p2 -b .jemalloc-ppc.patch
%patch6 -p1 -b .webrtc-arch-cpu
%patch7 -p1 -b .no-format
%patch8 -p2 -b .ppc64le
%if %{?debug_build}
%patch9 -p1 -b .debug
%endif
%patch10 -p1 -b .nss-3.19.1
%patch11 -p1 -b .nspr-prbool

# RPM specific patches
%patch101 -p1 -b .default
%patch102 -p1 -b .addons
%patch103 -p1 -b .rhbz-966424
%patch106 -p2 -b .plugins
%patch108 -p1 -b .rhbz-1014858
%patch109 -p1 -b .aarch64

# For branding specific patches.
%patch200 -p1 -b .duckduckgo
%patch201 -p1 -b .mozbz-1005535
%patch202 -p1 -b .mozbz-1152515
%patch203 -p1 -b .mozilla-1204147

# Upstream patches

%if %{official_branding}
# Required by Mozilla Corporation

%else
# Not yet approved by Mozilla Corporation

%endif


%{__rm} -f .mozconfig
%{__cp} %{SOURCE10} .mozconfig
%if %{official_branding}
%{__cat} %{SOURCE11} >> .mozconfig
%endif
%{__cp} %{SOURCE24} mozilla-api-key

%if %{?system_sqlite}
echo "ac_add_options --enable-system-sqlite" >> .mozconfig
%else
echo "ac_add_options --disable-system-sqlite" >> .mozconfig
%endif

echo "ac_add_options --with-system-libvpx" >> .mozconfig

%if %{?system_cairo}
echo "ac_add_options --enable-system-cairo" >> .mozconfig
%else
echo "ac_add_options --disable-system-cairo" >> .mozconfig
%endif

%if %{?system_ffi}
echo "ac_add_options --enable-system-ffi" >> .mozconfig
%endif

%if %{?system_nss}
echo "ac_add_options --with-system-nspr" >> .mozconfig
echo "ac_add_options --with-system-nss" >> .mozconfig
%else
echo "ac_add_options --without-system-nspr" >> .mozconfig
echo "ac_add_options --without-system-nss" >> .mozconfig
%endif

%if %{?enable_gstreamer}
echo "ac_add_options --enable-gstreamer=1.0" >> .mozconfig
%else
echo "ac_add_options --disable-gstreamer" >> .mozconfig
%endif

%ifnarch %{ix86} x86_64
echo "ac_add_options --disable-methodjit" >> .mozconfig
echo "ac_add_options --disable-monoic" >> .mozconfig
echo "ac_add_options --disable-polyic" >> .mozconfig
echo "ac_add_options --disable-tracejit" >> .mozconfig
%endif

# RHEL 7 mozconfig changes:
echo "ac_add_options --enable-system-hunspell" >> .mozconfig
echo "ac_add_options --enable-libnotify" >> .mozconfig
echo "ac_add_options --enable-startup-notification" >> .mozconfig
echo "ac_add_options --enable-jemalloc" >> .mozconfig

# Debug build flags
%if %{?debug_build}
echo "ac_add_options --enable-debug" >> .mozconfig
echo "ac_add_options --disable-optimize" >> .mozconfig
%else
echo "ac_add_options --disable-debug" >> .mozconfig
echo "ac_add_options --enable-optimize" >> .mozconfig
%endif

#---------------------------------------------------------------------

%build
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

cd %{tarballdir}

# Mozilla builds with -Wall with exception of a few warnings which show up
# everywhere in the code; so, don't override that.
MOZ_OPT_FLAGS=$(echo "$RPM_OPT_FLAGS -fpermissive" | %{__sed} -e 's/-Wall//')
%if %{?debug_build}
MOZ_OPT_FLAGS=$(echo "$MOZ_OPT_FLAGS" | %{__sed} -e 's/-O2//')
%endif
# -Werror=format-security causes build failures when -Wno-format is explicitly given
# for some sources
MOZ_OPT_FLAGS="$MOZ_OPT_FLAGS -Wformat-security -Wformat -Werror=format-security"

%ifarch s390
MOZ_OPT_FLAGS=$(echo "$RPM_OPT_FLAGS" | %{__sed} -e 's/-g/-g1/')
%endif
%ifarch s390 %{arm} ppc
MOZ_LINK_FLAGS="-Wl,--no-keep-memory -Wl,--reduce-memory-overheads"
%endif

export CFLAGS=$(echo "$MOZ_OPT_FLAGS" | %{__sed} -e 's/-fpermissive//')
export CXXFLAGS=$MOZ_OPT_FLAGS
export LDFLAGS=$MOZ_LINK_FLAGS

export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

MOZ_SMP_FLAGS=-j1
%ifnarch ppc ppc64 s390 s390x
[ -z "$RPM_BUILD_NCPUS" ] && \
     RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"
[ "$RPM_BUILD_NCPUS" -ge 2 ] && MOZ_SMP_FLAGS=-j2
[ "$RPM_BUILD_NCPUS" -ge 4 ] && MOZ_SMP_FLAGS=-j4
[ "$RPM_BUILD_NCPUS" -ge 8 ] && MOZ_SMP_FLAGS=-j8
%endif

MOZ_APP_DIR=%{_libdir}/%{name}
make -f client.mk build STRIP="/bin/true" MOZ_MAKE_FLAGS="$MOZ_SMP_FLAGS"

#---------------------------------------------------------------------

%install
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

# set up the firefox start script
rm -rf $RPM_BUILD_ROOT%{_bindir}/firefox
cp %{SOURCE21} $RPM_BUILD_ROOT%{_bindir}/firefox
%{__chmod} 755 $RPM_BUILD_ROOT%{_bindir}/firefox

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
%{__tar} xf %{SOURCE1}
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

# System extensions
%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/mozilla/extensions/%{firefox_app_id}
%{__mkdir_p} $RPM_BUILD_ROOT%{_libdir}/mozilla/extensions/%{firefox_app_id}

# Copy over the LICENSE
%{__install} -p -c -m 644 LICENSE $RPM_BUILD_ROOT/%{mozappdir}

# Use the system hunspell dictionaries for RHEL6+
%{__rm} -rf ${RPM_BUILD_ROOT}%{mozappdir}/dictionaries
ln -s %{_datadir}/myspell ${RPM_BUILD_ROOT}%{mozappdir}/dictionaries

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

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files -f %{name}.lang
%defattr(-,root,root,-)
%{_bindir}/firefox
%doc %{_mandir}/man1/*
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
%dir %{mozappdir}/browser/components
%{mozappdir}/browser/components/*.so
%{mozappdir}/browser/components/*.manifest
%attr(644, root, root) %{mozappdir}/browser/blocklist.xml
%dir %{mozappdir}/browser/extensions
%{mozappdir}/browser/extensions/{972ce4c6-7e08-4474-a285-3208198ce6fd}
%dir %{mozappdir}/langpacks
%{mozappdir}/browser/icons
%{mozappdir}/browser/searchplugins
%{mozappdir}/browser/omni.ja
%{mozappdir}/firefox
%{mozappdir}/firefox-bin
%{mozappdir}/run-mozilla.sh
%{mozappdir}/application.ini
%{mozappdir}/defaults/preferences/*
%{mozappdir}/browser/defaults/preferences
%exclude %{mozappdir}/removed-files
%{mozappdir}/webapprt-stub
%dir %{mozappdir}/webapprt
%{mozappdir}/webapprt/omni.ja
%{mozappdir}/webapprt/webapprt.ini
%{mozappdir}/chrome.manifest
%{mozappdir}/components/*.so
%{mozappdir}/components/*.manifest
%{mozappdir}/dictionaries
%{mozappdir}/*.so
%{mozappdir}/omni.ja
%{mozappdir}/platform.ini
%{mozappdir}/plugin-container
%{mozappdir}/dependentlibs.list
%exclude %{mozappdir}/defaults/pref/channel-prefs.js
%{mozappdir}/gmp-clearkey
%if !%{?system_nss}
%{mozappdir}/*.chk
%endif

#we don't ship firefox-devel package
%exclude %{_datadir}/idl/*
%exclude %{_includedir}/*
%exclude %{_libdir}/%{name}-devel-*/*

#---------------------------------------------------------------------

%changelog
* Wed Nov 04 2015 CentOS Sources <bugs@centos.org> - 38.4.0-1.el7.centos
- CentOS default prefs

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
