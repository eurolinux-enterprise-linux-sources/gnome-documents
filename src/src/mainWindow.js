/*
 * Copyright (c) 2011 Red Hat, Inc.
 *
 * Gnome Documents is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by the
 * Free Software Foundation; either version 2 of the License, or (at your
 * option) any later version.
 *
 * Gnome Documents is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
 * or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
 * for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with Gnome Documents; if not, write to the Free Software Foundation,
 * Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * Author: Cosimo Cecchi <cosimoc@redhat.com>
 *
 */

const Gdk = imports.gi.Gdk;
const GLib = imports.gi.GLib;
const Gtk = imports.gi.Gtk;

const Lang = imports.lang;
const Mainloop = imports.mainloop;

const Application = imports.application;
const Config = imports.config;
const Embed = imports.embed;
const Selections = imports.selections;
const Utils = imports.utils;
const WindowMode = imports.windowMode;

const _ = imports.gettext.gettext;

const _CONFIGURE_ID_TIMEOUT = 100; // msecs
const _WINDOW_MIN_WIDTH = 600;
const _WINDOW_MIN_HEIGHT = 500;

const MainWindow = new Lang.Class({
    Name: 'MainWindow',

    _init: function(app) {
        this._configureId = 0;

        this.window = new Gtk.ApplicationWindow({ application: app,
                                                  width_request: _WINDOW_MIN_WIDTH,
                                                  height_request: _WINDOW_MIN_HEIGHT,
						  window_position: Gtk.WindowPosition.CENTER,
						  title: _("Documents") });

        // apply the last saved window size and position
        let size = Application.settings.get_value('window-size');
        if (size.n_children() == 2) {
            let width = size.get_child_value(0);
            let height = size.get_child_value(1);

            this.window.set_default_size(width.get_int32(),
                                         height.get_int32());
        }

        let position = Application.settings.get_value('window-position');
        if (position.n_children() == 2) {
            let x = position.get_child_value(0);
            let y = position.get_child_value(1);

            this.window.move(x.get_int32(),
                             y.get_int32());
        }

        if (Application.settings.get_boolean('window-maximized'))
            this.window.maximize();

        this.window.connect('delete-event',
                            Lang.bind(this, this._quit));
        this.window.connect('button-press-event',
                            Lang.bind(this, this._onButtonPressEvent));
        this.window.connect('key-press-event',
                            Lang.bind(this, this._onKeyPressEvent));
        this.window.connect('configure-event',
                            Lang.bind(this, this._onConfigureEvent));
        this.window.connect('window-state-event',
                            Lang.bind(this, this._onWindowStateEvent));

        this._fsId = Application.modeController.connect('fullscreen-changed',
            Lang.bind(this, this._onFullscreenChanged));

        this._embed = new Embed.Embed();
        this.window.add(this._embed.widget);
    },

    _saveWindowGeometry: function() {
        let window = this.window.get_window();
        let state = window.get_state();

        if (state & Gdk.WindowState.MAXIMIZED)
            return;

        // GLib.Variant.new() can handle arrays just fine
        let size = this.window.get_size();
        let variant = GLib.Variant.new ('ai', size);
        Application.settings.set_value('window-size', variant);

        let position = this.window.get_position();
        variant = GLib.Variant.new ('ai', position);
        Application.settings.set_value('window-position', variant);
    },

    _onConfigureEvent: function(widget, event) {
        if (Application.modeController.getFullscreen())
            return;

        if (this._configureId != 0) {
            Mainloop.source_remove(this._configureId);
            this._configureId = 0;
        }

        this._configureId = Mainloop.timeout_add(_CONFIGURE_ID_TIMEOUT, Lang.bind(this,
            function() {
                this._configureId = 0;
                this._saveWindowGeometry();
                return false;
            }));
    },

    _onWindowStateEvent: function(widget, event) {
        let window = widget.get_window();
        let state = window.get_state();

        if (state & Gdk.WindowState.FULLSCREEN)
            return;

        let maximized = (state & Gdk.WindowState.MAXIMIZED);
        Application.settings.set_boolean('window-maximized', maximized);
    },

    _onFullscreenChanged: function(controller, fullscreen) {
        if (fullscreen)
            this.window.fullscreen();
        else
            this.window.unfullscreen();
    },

    _goBack: function() {
        let windowMode = Application.modeController.getWindowMode();
        let activeCollection = Application.collectionManager.getActiveItem();
        let handled = true;

        if (windowMode == WindowMode.WindowMode.PREVIEW ||
            windowMode == WindowMode.WindowMode.EDIT) {
            Application.documentManager.setActiveItem(null);
        } else if (windowMode == WindowMode.WindowMode.OVERVIEW && activeCollection) {
            Application.documentManager.activatePreviousCollection();
        } else {
            handled = false;
        }

        return handled;
    },

    _onButtonPressEvent: function(widget, event) {
        let button = event.get_button()[1];
        let clickCount = event.get_click_count()[1];

        if (clickCount > 1)
            return false;

        // mouse back button
        if (button != 8)
            return false;

        return this._goBack();
    },

    _onKeyPressEvent: function(widget, event) {
        if (this._handleBackKey(event))
            return true;

        let toolbar = this._embed.getMainToolbar();
        if (toolbar.handleEvent(event))
            return true;

        switch (Application.modeController.getWindowMode()) {
        case WindowMode.WindowMode.NONE:
            return false;
        case WindowMode.WindowMode.PREVIEW:
            return this._handleKeyPreview(event);
        case WindowMode.WindowMode.OVERVIEW:
            return this._handleKeyOverview(event);
        case WindowMode.WindowMode.EDIT:
            return false;
        default:
            throw(new Error('Not handled'));
            break;
        }

        return false;
    },

    _isBackKey: function(event) {
        let direction = this.window.get_direction();
        let keyval = event.get_keyval()[1];
        let state = event.get_state()[1];

        let isBack = (((state & Gdk.ModifierType.MOD1_MASK) != 0 &&
                       ((direction == Gtk.TextDirection.LTR && keyval == Gdk.KEY_Left) ||
                       (direction == Gtk.TextDirection.RTL && keyval == Gdk.KEY_Right))) ||
                      keyval == Gdk.KEY_Back);

        return isBack;
    },

    _handleBackKey: function(event) {
        let isBack = this._isBackKey(event);
        if (!isBack)
            return false;

        return this._goBack();
    },

    _handleKeyPreview: function(event) {
        let keyval = event.get_keyval()[1];
        let fullscreen = Application.modeController.getFullscreen();
        let def_mod_mask = Gtk.accelerator_get_default_mod_mask();
        let preview = this._embed.getPreview();
        let state = event.get_state()[1];

        if (keyval == Gdk.KEY_Escape) {
            let model = preview.getModel();

            if (preview.controlsVisible && (model != null))
                preview.controlsVisible = false;
            else if (fullscreen)
                Application.documentManager.setActiveItem(null);

            return false;
        }

        if (((keyval == Gdk.KEY_Page_Up) &&
            ((state & Gdk.ModifierType.CONTROL_MASK) != 0)) ||
            ((keyval == Gdk.KEY_Left) && ((state & def_mod_mask) == 0))) {
            preview.view.previous_page();
            return true;
        }

        if (((keyval == Gdk.KEY_Page_Down) &&
            ((state & Gdk.ModifierType.CONTROL_MASK) != 0)) ||
            ((keyval == Gdk.KEY_Right) && ((state & def_mod_mask) == 0))) {
            preview.view.next_page();
            return true;
        }

        if (keyval == Gdk.KEY_Page_Up) {
            preview.view.scroll(Gtk.ScrollType.PAGE_BACKWARD, false);
            return true;
        }

        if (keyval == Gdk.KEY_space ||
            keyval == Gdk.KEY_Page_Down) {
            preview.view.scroll(Gtk.ScrollType.PAGE_FORWARD, false);
            return true;
        }

        return false;
    },

    _handleKeyOverview: function(event) {
        let keyval = event.get_keyval()[1];

        if (Application.selectionController.getSelectionMode() &&
            keyval == Gdk.KEY_Escape) {
            Application.selectionController.setSelectionMode(false);
            return true;
        }

        return false;
    },

    _quit: function() {
        // remove configure event handler if still there
        if (this._configureId != 0) {
            Mainloop.source_remove(this._configureId);
            this._configureId = 0;
        }

        // always save geometry before quitting
        this._saveWindowGeometry();

        return false;
    },

    showAbout: function() {
        let aboutDialog = new Gtk.AboutDialog();

        aboutDialog.artists = [ 'Jakub Steiner <jimmac@gmail.com>' ];
        aboutDialog.authors = [ 'Cosimo Cecchi <cosimoc@gnome.org>',
                                'Florian M' + String.fromCharCode(0x00FC) + 'llner <fmuellner@gnome.org>',
                                'William Jon McCann <william.jon.mccann@gmail.com>' ];
        aboutDialog.translator_credits = _("translator-credits");
        aboutDialog.program_name = _("Documents");
        aboutDialog.comments = _("A document manager application");
        aboutDialog.copyright = 'Copyright ' + String.fromCharCode(0x00A9) + ' 2011' + String.fromCharCode(0x2013) + '2012 Red Hat, Inc.';
        aboutDialog.license_type = Gtk.License.GPL_2_0;
        aboutDialog.logo_icon_name = 'gnome-documents';
        aboutDialog.version = Config.PACKAGE_VERSION;
        aboutDialog.website = 'https://wiki.gnome.org/Apps/Documents';
        aboutDialog.wrap_license = true;

        aboutDialog.modal = true;
        aboutDialog.transient_for = this.window;

        aboutDialog.show();
        aboutDialog.connect('response', function() {
            aboutDialog.destroy();
        });
    }
});
