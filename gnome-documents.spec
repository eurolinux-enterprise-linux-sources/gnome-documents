%define evince_version 3.13.3
%define gtk3_version 3.13.2

Name:           gnome-documents
Version:        3.14.3
Release:        3%{?dist}
Summary:        A document manager application for GNOME

License:        GPLv2+
URL:            https://live.gnome.org/Design/Apps/Documents
Source0:        http://download.gnome.org/sources/%{name}/3.14/%{name}-%{version}.tar.xz

# https://bugzilla.redhat.com/show_bug.cgi?id=1057160
Patch0:         gnome-documents-show-a-back-button-while-loading.patch
# https://bugzilla.redhat.com/show_bug.cgi?id=958690
Patch1:         gnome-documents-prevent-nested-collections.patch

Patch100:       translations.patch

BuildRequires:  evince-devel >= %{evince_version}
BuildRequires:  gtk3-devel >= %{gtk3_version}
BuildRequires:  intltool
BuildRequires:  libgdata-devel
BuildRequires:  gnome-desktop3-devel
BuildRequires:  liboauth-devel
BuildRequires:  gnome-online-accounts-devel
BuildRequires:  tracker-devel >= 0.17.0
BuildRequires:  desktop-file-utils
BuildRequires:  gjs-devel
BuildRequires:  libzapojit-devel
BuildRequires:  webkitgtk3-devel
BuildRequires:  itstool
BuildRequires:  inkscape
BuildRequires:  poppler-utils
BuildRequires:  docbook-style-xsl

Requires:       evince-libs%{?_isa} >= %{evince_version}
Requires:       gtk3%{?_isa} >= %{gtk3_version}
Requires:       gnome-online-miners

%description
gnome-documents is a document manager application for GNOME,
aiming to be a simple and elegant replacement for using Files to show
the Documents directory.

%prep
%setup -q
%patch0 -p1 -b .back-button-loading
%patch1 -p1 -b .nested-collections
%patch100 -p1 -b .translations

%build
%configure --disable-static --enable-getting-started
make %{?_smp_mflags}

%install
make install DESTDIR=$RPM_BUILD_ROOT
find $RPM_BUILD_ROOT -name '*.la' -exec rm -f {} ';'
desktop-file-validate $RPM_BUILD_ROOT/%{_datadir}/applications/org.gnome.Documents.desktop
%find_lang %{name} --with-gnome


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
%doc README AUTHORS NEWS TODO COPYING
%{_datadir}/%{name}
%{_bindir}/%{name}
%{_datadir}/appdata/org.gnome.Documents.appdata.xml
%{_datadir}/dbus-1/services/*
%{_datadir}/glib-2.0/schemas/*
%{_datadir}/applications/*
%{_datadir}/icons/hicolor/*/apps/gnome-documents.png
%{_libdir}/gnome-documents/
%{_mandir}/man1/%{name}.1.gz
# co-own these directories
%dir %{_datadir}/gnome-shell
%dir %{_datadir}/gnome-shell/search-providers
%{_datadir}/gnome-shell/search-providers/org.gnome.Documents.search-provider.ini

%changelog
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

