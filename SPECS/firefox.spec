# Use system sqlite?
%define system_sqlite           1
%define system_ffi              0

# Use system nss/nspr?
%define system_nss              1

# Enable webm for i686/x86_64 only
%ifarch %{ix86} x86_64
%define enable_webm             1
%else
%define enable_webm             0
%endif

# Use system cairo?
%define system_cairo            0

# Build as a debug package?
%define debug_build             0

# Do we build a final version?
%define official_branding       1

# Minimal required versions
%if %{?system_nss}
%define nspr_version 4.10.2
%define nss_version 3.15.4
%endif

%define cairo_version 1.10.2
%define freetype_version 2.1.9

# Bookmark variables
%define default_bookmarks_file  %{_datadir}/bookmarks/default-bookmarks.html
%define firefox_app_id          \{ec8030f7-c20a-464f-9b0e-13a3a9e97384\}

%define mozappdir               %{_libdir}/%{name}
%define langpackdir             %{mozappdir}/langpacks

%if %{?system_sqlite}
%define sqlite_version 3.6.22
# The actual sqlite version (see #480989):
%global sqlite_build_version %(pkg-config --silence-errors --modversion sqlite3 2>/dev/null || echo 65536)
%endif

%define official_branding       1
%define build_langpacks         1

%if %{official_branding}
%define tarballdir  mozilla-esr24
%define ext_version esr
%endif

Summary:        Mozilla Firefox Web browser
Name:           firefox
Version:        24.8.0
Release:        1%{?prever}%{?dist}
URL:            http://www.mozilla.org/projects/firefox/
License:        MPLv1.1 or GPLv2+ or LGPLv2+
Group:          Applications/Internet
# From ftp://ftp.mozilla.org/pub/firefox/releases/%{version}%{?pretag}/source
Source0:        firefox-%{version}%{?prever}%{?ext_version}.source.tar.bz2
%if %{build_langpacks}
Source1:        firefox-langpacks-%{version}%{?ext_version}-20140826.tar.bz2
%endif
Source10:       firefox-mozconfig
Source11:       firefox-mozconfig-branded
Source12:       firefox-redhat-default-prefs.js
Source20:       firefox.desktop
Source21:       firefox.sh.in
Source23:       firefox.1
Source100:      find-external-requires

# Build patches
Patch0:         firefox-install-dir.patch
Patch4:         xulrunner-24.0-gcc47.patch
Patch5:         xulrunner-24.0-jemalloc-ppc.patch

# RPM specific patches
Patch11:        firefox-24.0-default.patch
Patch12:        firefox-17.0-enable-addons.patch
Patch13:        rhbz-966424.patch
Patch14:        rhbz-1032770.patch
Patch15:        firefox-system-nss-3.16.2.patch

# RHEL patches
Patch100:       firefox-5.0-asciidel.patch
Patch200:       firefox-duckduckgo.patch

# Upstream patches
Patch300:       mozilla-906754.patch

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
Requires:       system-bookmarks
Requires:       redhat-indexhtml

%if %{?enable_webm}
BuildRequires:  libvpx-devel >= 1.0.0
Requires:       libvpx >= 1.0.0
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

%if %{?system_cairo}
BuildRequires:  cairo-devel >= %{cairo_version}
%endif

BuildRequires:  hunspell-devel
Requires:       mozilla-filesystem
%if %{?system_sqlite}
BuildRequires:  sqlite-devel >= %{sqlite_version}
Requires:       sqlite >= %{sqlite_build_version}
%endif

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

# Build patches
# We have to keep original patch backup extension to go thru configure without problems with tests
%patch0 -p1 -b .orig
%patch4 -p2 -b .gcc47.patch
%patch5 -p2 -b .jemalloc-ppc.patch

# RPM specific patches
%patch11 -p2 -b .default
%patch12 -p1 -b .addons
%patch13 -p1 -b .rhbz-966424
%patch14 -p1 -b .rhbz-1032770
%patch15 -p2 -b .nss-3.16.2

# RHEL patches
%patch100 -p1 -b .asciidel
%patch200 -p1 -b .duckduckgo

# Upstream patches
%patch300 -p1 -b .906754

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

%if %{?system_sqlite}
echo "ac_add_options --enable-system-sqlite" >> .mozconfig
%else
echo "ac_add_options --disable-system-sqlite" >> .mozconfig
%endif

%if %{?enable_webm}
echo "ac_add_options --with-system-libvpx" >> .mozconfig
echo "ac_add_options --enable-webm" >> .mozconfig
echo "ac_add_options --enable-webrtc" >> .mozconfig
echo "ac_add_options --enable-ogg" >> .mozconfig
%else
echo "ac_add_options --without-system-libvpx" >> .mozconfig
echo "ac_add_options --disable-webm" >> .mozconfig
echo "ac_add_options --disable-webrtc" >> .mozconfig
echo "ac_add_options --disable-ogg" >> .mozconfig
%endif

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

%ifnarch %{ix86} x86_64
echo "ac_add_options --disable-methodjit" >> .mozconfig
echo "ac_add_options --disable-monoic" >> .mozconfig
echo "ac_add_options --disable-polyic" >> .mozconfig
echo "ac_add_options --disable-tracejit" >> .mozconfig
%endif

# RHEL 6 mozconfig changes:
echo "ac_add_options --enable-system-hunspell" >> .mozconfig
echo "ac_add_options --enable-libnotify" >> .mozconfig
echo "ac_add_options --enable-startup-notification" >> .mozconfig
echo "ac_add_options --enable-jemalloc" >> .mozconfig

# s390(x) fails to start with jemalloc enabled
%ifarch s390 s390x ppc ppc64
echo "ac_add_options --disable-jemalloc" >> .mozconfig
%endif

# Debug build flags
%if %{?debug_build}
echo "ac_add_options --enable-debug" >> .mozconfig
echo "ac_add_options --disable-optimize" >> .mozconfig
echo "ac_add_options --enable-dtrace" >> .mozconfig
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
%ifarch s390
MOZ_OPT_FLAGS=$(echo "$RPM_OPT_FLAGS" | %{__sed} -e 's/-g/-g1/')
%endif
%ifarch s390 %{arm} ppc
MOZ_LINK_FLAGS="-Wl,--no-keep-memory -Wl,--reduce-memory-overheads"
%endif

export CFLAGS=$MOZ_OPT_FLAGS
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

# set up our prefs and add it to the package manifest file, so it gets pulled in
# to omni.jar which gets created during make install
%{__cp} %{SOURCE12} objdir/dist/bin/browser/defaults/preferences/all-redhat.js
# This sed call "replaces" firefox.js with all-redhat.js, newline, and itself (&)
# having the net effect of prepending all-redhat.js above firefox.js
%{__sed} -i -e\
    's|@BINPATH@/browser/@PREF_DIR@/firefox.js|@BINPATH@/browser/@PREF_DIR@/all-redhat.js\n&|' \
    browser/installer/package-manifest.in

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
%endif # build_langpacks

# Keep compatibility with the old preference location.
%{__mkdir_p} $RPM_BUILD_ROOT/%{mozappdir}/defaults/preferences
%{__mkdir_p} $RPM_BUILD_ROOT/%{mozappdir}/browser/defaults
ln -s %{mozappdir}/defaults/preferences $RPM_BUILD_ROOT/%{mozappdir}/browser/defaults/preferences

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

%preun
# is it a final removal?
if [ $1 -eq 0 ]; then
  %{__rm} -rf %{mozappdir}/components
  %{__rm} -rf %{mozappdir}/extensions
  %{__rm} -rf %{mozappdir}/langpacks
  %{__rm} -rf %{mozappdir}/plugins
fi

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
%dir %{mozappdir}/defaults/preferences
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
%{mozappdir}/mozilla-xremote-client
%{mozappdir}/omni.ja
%{mozappdir}/platform.ini
%{mozappdir}/plugin-container
%{mozappdir}/dependentlibs.list
%exclude %{mozappdir}/defaults/pref/channel-prefs.js

#we don't ship firefox-devel package
%exclude %{_datadir}/idl/*
%exclude %{_includedir}/*
%exclude %{_libdir}/%{name}-devel-*/*

#---------------------------------------------------------------------

%changelog
* Tue Aug 26 2014 Martin Stransky <stransky@redhat.com> - 24.8.0-1
- Update to 24.8.0 ESR

* Thu Jul 17 2014 Jan Horak <jhorak@redhat.com> - 24.7.0-1
- Update to 24.7.0 ESR

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

