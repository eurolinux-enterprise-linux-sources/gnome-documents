%define evince_version 3.13.3
%define gettext_version 0.19.8
%define gjs_version 1.48.0
%define gtk3_version 3.22.15
%define tracker_version 0.17.3
%define libgepub_version 0.6

Name:           gnome-documents
Version:        3.28.2
Release:        2%{?dist}
Summary:        A document manager application for GNOME

License:        GPLv2+
URL:            https://wiki.gnome.org/Apps/Documents
Source0:        https://download.gnome.org/sources/%{name}/3.28/%{name}-%{version}.tar.xz

# Fix the build with Python 2
Patch1:         gnome-documents-python2.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=985887
# https://bugzilla.redhat.com/show_bug.cgi?id=1444437
Patch2:         gnome-documents-skydrive-and-lok-fixes.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1569793
Patch3:         gnome-documents-tracker.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1611565
Patch4:         gnome-documents-dont-attempt-to-load-collections.patch

# https://bugzilla.redhat.com/show_bug.cgi?id=1690935
Patch5:         gnome-documents-meson.build-allow-libgdprivate-1.0.so-to-find-libgd.patch

BuildRequires:  pkgconfig(evince-document-3.0) >= %{evince_version}
BuildRequires:  pkgconfig(evince-view-3.0) >= %{evince_version}
BuildRequires:  pkgconfig(webkit2gtk-4.0)
BuildRequires:  pkgconfig(gtk+-3.0) >= %{gtk3_version}
BuildRequires:  pkgconfig(gjs-1.0) >= %{gjs_version}
BuildRequires:  pkgconfig(tracker-control-1.0) >= %{tracker_version}
BuildRequires:  pkgconfig(tracker-sparql-1.0) >= %{tracker_version}
BuildRequires:  pkgconfig(goa-1.0)
BuildRequires:  pkgconfig(gnome-desktop-3.0)
BuildRequires:  pkgconfig(libgdata)
BuildRequires:  pkgconfig(libgepub-0.6) >= %{libgepub_version}
BuildRequires:  pkgconfig(zapojit-0.0)
BuildRequires:  pkgconfig(libsoup-2.4)
BuildRequires:  liboauth-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gettext >= %{gettext_version}
BuildRequires:  itstool
BuildRequires:  inkscape
BuildRequires:  meson
BuildRequires:  poppler-utils
BuildRequires:  docbook-style-xsl

Requires:       evince-libs%{?_isa} >= %{evince_version}
Requires:       gettext%{?isa} >= %{gettext_version}
Requires:       gjs%{?_isa} >= %{gjs_version}
Requires:       gtk3%{?_isa} >= %{gtk3_version}
Requires:       gnome-online-miners
Requires:       libgepub%{?_isa} >= %{libgepub_version}
Requires:       libreofficekit
Requires:       %{name}-libs%{?_isa} = %{version}-%{release}

%description
gnome-documents is a document manager application for GNOME,
aiming to be a simple and elegant replacement for using Files to show
the Documents directory.

%package libs
Summary: Common libraries and data files for %{name}
%description libs
%{summary}.

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1

%build
%meson -Dgetting_started=true
%meson_build

%install
%meson_install

# Disable gnome-books
rm -f $RPM_BUILD_ROOT/%{_bindir}/gnome-books
rm -f $RPM_BUILD_ROOT/%{_datadir}/dbus-1/services/org.gnome.Books.service
rm -f $RPM_BUILD_ROOT/%{_datadir}/glib-2.0/schemas/org.gnome.books.gschema.xml
rm -f $RPM_BUILD_ROOT/%{_datadir}/applications/org.gnome.Books.desktop
rm -f $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/*/apps/org.gnome.Books.png
rm -f $RPM_BUILD_ROOT/%{_datadir}/icons/hicolor/scalable/apps/org.gnome.Books-symbolic.svg
rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/gnome-books.1*
rm -f $RPM_BUILD_ROOT/%{_datadir}/metainfo/org.gnome.Books.appdata.xml

%find_lang %{name} --with-gnome

%check
desktop-file-validate $RPM_BUILD_ROOT%{_datadir}/applications/org.gnome.Documents.desktop

%post
/sbin/ldconfig
touch --no-create %{_datadir}/icons/hicolor >&/dev/null || :

%postun
/sbin/ldconfig
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor >&/dev/null || :
    gtk-update-icon-cache %{_datadir}/icons/hicolor >&/dev/null || :
    /usr/bin/glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor >&/dev/null || :
/usr/bin/glib-compile-schemas %{_datadir}/glib-2.0/schemas &> /dev/null || :

%files -f %{name}.lang
%license COPYING
%doc README AUTHORS NEWS TODO
%{_bindir}/%{name}
%{_datadir}/dbus-1/services/org.gnome.Documents.service
%{_datadir}/glib-2.0/schemas/org.gnome.documents.gschema.xml
%{_datadir}/applications/org.gnome.Documents.desktop
%{_datadir}/icons/hicolor/*/apps/org.gnome.Documents.png
%{_datadir}/icons/hicolor/scalable/apps/org.gnome.Documents-symbolic.svg
%{_mandir}/man1/gnome-documents.1*
# co-own these directories
%dir %{_datadir}/gnome-shell
%dir %{_datadir}/gnome-shell/search-providers
%{_datadir}/gnome-shell/search-providers/org.gnome.Documents.search-provider.ini
%{_datadir}/metainfo/org.gnome.Documents.appdata.xml

%files libs
%{_datadir}/%{name}
%{_datadir}/glib-2.0/schemas/org.gnome.Documents.enums.xml
%{_libdir}/gnome-documents/

%changelog
* Wed Mar 20 2019 Debarshi Ray <rishi@fedoraproject.org> - 3.28.2-2
- Make documents show up when started through search provider
  Resolves: #1690935

* Fri Aug 24 2018 Debarshi Ray <rishi@fedoraproject.org> - 3.28.2-1
- Update to 3.28.2
- Rebased downstream patches
- Fix crash on right-click on local collection
  Resolves: #1611565

* Tue Aug 14 2018 Debarshi Ray <rishi@fedoraproject.org> - 3.28.1-2
- Stop the garbage collector from complaining during shutdown
  Resolves: #1608936

* Wed Jun 06 2018 Debarshi Ray <rishi@fedoraproject.org> - 3.28.1-1
- Update to 3.28.1
- Rebased downstream patches
- Revert to using Python 2 and Tracker 1.0
- Resolves: #1568171

* Tue Dec 12 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-8
- Initialize the getting started PDF only when presenting a UI, and before any
  SPARQL has been submitted
- Suppress WARNINGs from GJS 1.50.0 by using var instead of let/const for
  exported symbols
- Use the standard dialect of String.prototype.replace
  Resolves: #1517770

* Wed Dec 06 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-7
- Suppress WARNINGs from GJS 1.50.0 about replacing GObject signal methods
  Resolves: #1517770

* Mon Nov 27 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-6
- Adjust the LOKDocView detection to work with GJS 1.48.0
- Suppress WARNINGs from GJS 1.50.0 by using var instead of let/const for
  exported symbols
  Resolves: #1517704

* Fri Jun 09 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-5
- Fix CRITICALs on invoking the application when a primary instance is present
  Resolves: #1436566

* Thu May 11 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-4
- Fix crash on repeated opening of presentations
  Resolves: #1444437

* Fri Apr 21 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-3
- Disable the print button in the selection toolbar when printing isn't
  supported
  Resolves: #1438362

* Tue Apr 04 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-2
- Unable to preview LOKDocView-supported documents from OneDrive
  Resolves: #1436682

* Mon Mar 27 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.2-1
- Update to 3.22.2
- Thumbnail OneDrive entries once they are loaded
  Resolves: #985887, #1386892

* Wed Mar 22 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.1-2
- Drop gnome-books due to unavailability of gnome-epub-thumbnailer
  Resolves: #1433418

* Sun Mar 12 2017 Debarshi Ray <rishi@fedoraproject.org> - 3.22.1-1
- Update to 3.22.1
  Resolves: #1386892

* Wed Jun 15 2016 Debarshi Ray <rishi@fedoraproject.org> - 3.14.3-3
- Prevent nested collections
  Resolves: #958690

* Wed May 20 2015 Debarshi Ray <rishi@fedoraproject.org> - 3.14.3-2
- Show a back button when loading
  Resolves: #1057160

* Fri May 15 2015 Debarshi Ray <rishi@fedoraproject.org> - 3.14.3-1
- Update to 3.14.3
  Update translations
  Resolves: #1174601

* Mon Mar 23 2015 Richard Hughes <rhughes@redhat.com> - 3.14.2-1
- Update to 3.14.2
  Resolves: #1174601

* Fri Mar  7 2014 Debarshi Ray <rishi@fedoraproject.org> - 3.8.5-10
- get_pretty_name mixes up ASCII and UTF8 characters
  Resolves: #1073383

* Wed Feb 26 2014 Debarshi Ray <rishi@fedoraproject.org> - 3.8.5-9
- The sharing dialog is Google specific
  Resolves: #1062608

* Tue Feb 25 2014 Debarshi Ray <rishi@fedoraproject.org> - 3.8.5-8
- Fix the patch to preview encrypted PDFs
- Fix the patch to protect against spurious view-as signals
  Resolves: #959175

* Tue Feb 11 2014 Debarshi Ray <rishi@fedoraproject.org> - 3.8.5-7
- Use decimal instead of octal literal
  Resolves: #1035573

* Tue Feb 11 2014 Debarshi Ray <rishi@fedoraproject.org> - 3.8.5-6
- No indication of a document failing to print
  Resolves: #162299

* Mon Feb 10 2014 Debarshi Ray <rishi@fedoraproject.org> - 3.8.5-5
- Protect against spurious changed::view-as signals
  Resolves: #1056032

* Fri Jan 24 2014 Daniel Mach <dmach@redhat.com> - 3.8.5-4
- Mass rebuild 2014-01-24

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 3.8.5-3
- Mass rebuild 2013-12-27

* Wed Dec 11 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.5-2
- Update translations
  Resolves: #1030340

* Thu Oct 24 2013 Debarshi Ray <rishi@fedoraproject.org> - 3.8.5-1
- Update to 3.8.5

* Fri Aug 30 2013 Debarshi Ray <rishi@fedoraproject.org> - 3.8.4-1
- Update to 3.8.4

* Thu Jul 11 2013 Debarshi Ray <rishi@fedoraproject.org> - 3.8.3.1-2
- Backport support for previewing password protected PDFs (GNOME #700716)

* Fri Jun 14 2013 Debarshi Ray <rishi@fedoraproject.org> - 3.8.3.1-1
- Update to 3.8.3.1

* Sun Jun  9 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.3-1
- Update to 3.8.3

* Mon May 13 2013 Matthias Clasen <mclasen@redhat.com> - 3.8.2.1-1
- Update to 3.8.2.1

* Tue Apr 16 2013 Richard Hughes <rhughes@redhat.com> - 3.8.1-1
- Update to 3.8.1

* Thu Mar 28 2013 Cosimo Cecchi <cosimoc@gnome.org> - 3.8.0-2
- Enable generation of getting-started tutorial PDF

* Tue Mar 26 2013 Kalev Lember <kalevlember@gmail.com> - 3.8.0-1
- Update to 3.8.0

* Wed Mar 20 2013 Kalev Lember <kalevlember@gmail.com> - 3.7.92-1
- Update to 3.7.92

* Thu Mar  7 2013 Matthias Clasen <mclasen@redhat.com> - 3.7.91-1
- Update to 3.7.91

* Tue Feb 26 2013 Kalev Lember <kalevlember@gmail.com> - 3.7.90-1
- Update to 3.7.90

* Thu Feb 21 2013 Kalev Lember <kalevlember@gmail.com> - 3.7.5-3
- Rebuilt for cogl soname bump

* Wed Feb 20 2013 Kalev Lember <kalevlember@gmail.com> - 3.7.5-2
- Rebuilt for libgnome-desktop soname bump

* Thu Feb 07 2013 Richard Hughes <rhughes@redhat.com> - 3.7.5-1
- Update to 3.7.5

* Fri Jan 25 2013 Peter Robinson <pbrobinson@fedoraproject.org> 3.7.4-2
- Rebuild for new cogl

* Tue Jan 15 2013 Matthias Clasen <mclasen@redhat.com> - 3.7.4-1
- Update to 3.7.4

* Fri Dec 21 2012 Kalev Lember <kalevlember@gmail.com> - 3.7.3-1
- Update to 3.7.3

* Tue Nov 20 2012 Richard Hughes <hughsient@gmail.com> - 3.7.2-1
- Update to 3.7.2

* Tue Nov 13 2012 Kalev Lember <kalevlember@gmail.com> - 3.6.2-1
- Update to 3.6.2

* Mon Oct 15 2012 Cosimo Cecchi <cosimoc@redhat.com> - 3.6.1-1
- Update to 3.6.1

* Tue Sep 25 2012 Cosimo Cecchi <cosimoc@redhat.com> - 3.6.0-1
- Update to 3.6.0

* Tue Sep 18 2012 Cosimo Cecchi <cosimoc@redhat.com> - 3.5.92-1
- Update to 3.5.92

* Sun Sep 09 2012 Kalev Lember <kalevlember@gmail.com> - 3.5.91-2
- Rebuild against new cogl/clutter

* Tue Sep 04 2012 Cosimo Cecchi <cosimoc@redhat.com> - 3.5.91-1
- Update to 3.5.91

* Tue Aug 28 2012 Matthias Clasen <mclasen@redhat.com> - 3.5.90-2
- Rebuild against new cogl/clutter

* Tue Aug 21 2012 Elad Alfassa <elad@fedoraproject.org> - 3.5.90-1
- Update to latest upstream release

* Fri Aug 10 2012 Cosimo Cecchi <cosimoc@redhat.com> - 0.5.5-1
- Update to 0.5.5

* Thu Jul 19 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Jul 17 2012 Richard Hughes <hughsient@gmail.com> - 0.5.4-1
- Update to 0.5.4

* Wed Jun 27 2012 Cosimo Cecchi <cosimoc@redhat.com> - 0.5.3-1
- Update to 0.5.3

* Thu Jun 07 2012 Matthias Clasen <mclasen@redhat.com> - 0.5.2.1-2
- Rebuild

* Thu Jun 07 2012 Richard Hughes <hughsient@gmail.com> - 0.5.2.1-1
- Update to 0.5.2.1

* Sat May 05 2012 Kalev Lember <kalevlember@gmail.com> - 0.5.1-1
- Update to 0.5.1

* Tue Apr 17 2012 Kalev Lember <kalevlember@gmail.com> - 0.4.1-1
- Update to 0.4.1

* Mon Mar 26 2012 Cosimo Cecchi <cosimoc@redhat.com> - 0.4.0.1-1
- Update to 0.4.0.1

* Mon Mar 26 2012 Cosimo Cecchi <cosimoc@redhat.com> - 0.4.0-2
- Rebuild against current libevdocument3 soname

* Mon Mar 26 2012 Cosimo Cecchi <cosimoc@redhat.com> - 0.4.0-1
- Update to 0.4.0

* Wed Mar 21 2012 Kalev Lember <kalevlember@gmail.com> - 0.3.92-4
- Rebuild for libevdocument3 soname bump

* Tue Mar 20 2012 Adam Williamson <awilliam@redhat.com> - 0.3.92-3
- revert unoconv requirement, it pulls LO into the live image

* Tue Mar 20 2012 Adam Williamson <awilliam@redhat.com> - 0.3.92-2
- requires: unoconv (RHBZ #754516)

* Tue Mar 20 2012 Cosimo Cecchi <cosimoc@redhat.com> - 0.3.92-1
- Update to 0.3.92

* Sat Mar 10 2012 Matthias Clasen <mclasen@redhat.com> - 0.3.91-2
- Rebuild against new cogl

* Tue Mar 06 2012 Cosimo Cecchi <cosimoc@redhat.com> - 0.3.91-1
- Update to 0.3.91

* Sun Feb 26 2012 Matthias Clasen <mclasen@redhat.com> - 0.3.90-1
- Update to 0.3.90

* Thu Jan 19 2012 Matthias Clasen <mclasen@redhat.com> - 0.3.4-2
- Rebuild against new cogl

* Tue Jan 17 2012 Cosimo Cecchi <cosimoc@redhat.com> - 0.3.4-1
- Update to 0.3.4

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 20 2011 Matthias Clasen <mclasen@redhat.com> - 0.3.3-1
- Update to 0.3.3

* Wed Nov 23 2011 Matthias Clasen <mclasen@redhat.com> - 0.3.2-1
- Update to 0.3.2

* Tue Oct 18 2011 Elad Alfassa <elad@fedoraproject.org> - 0.2.1-1
- New upstream release

* Tue Sep 27 2011 Ray <rstrode@redhat.com> - 0.2.0-1
- Update to 0.2.0

* Tue Sep 20 2011 Matthias Clasen <mclasen@redhat.com> - 0.1.92-2
- Rebuild against newer clutter

* Tue Sep 20 2011 Elad Alfassa <elad@fedoraproject.org> - 0.1.92-1
- Update to 0.1.92

* Wed Sep  7 2011 Matthias Clasen <mclasen@redhat.com> - 0.1.91-1
- Update to 0.1.91

* Sat Sep 03 2011 Elad Alfassa <elad@fedoraproject.org> - 0.1.90-2
- Fix #735341

* Fri Sep 02 2011 Elad Alfassa <elad@fedoraproject.org> - 0.1.90-1
- Initial packaging.

