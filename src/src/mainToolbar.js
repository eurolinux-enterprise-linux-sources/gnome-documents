/*
 * Copyright (c) 2015 Alessandro Bono
 * Copyright (c) 2011, 2013, 2015 Red Hat, Inc.
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

const Gd = imports.gi.Gd;
const GLib = imports.gi.GLib;
const Gtk = imports.gi.Gtk;

const Gettext = imports.gettext;
const _ = imports.gettext.gettext;

const Lang = imports.lang;

const Application = imports.application;
const Searchbar = imports.searchbar;

var MainToolbar = new Lang.Class({
    Name: 'MainToolbar',
    Extends: Gtk.Box,

    _init: function() {
        this._model = null;
        this._handleEvent = true;

        this.parent({ orientation: Gtk.Orientation.VERTICAL });
        this.show();

        this.toolbar = new Gtk.HeaderBar({ hexpand: true });
        this.toolbar.get_style_context().add_class('titlebar');
        this.add(this.toolbar);
        this.toolbar.show();

        this.searchbar = this.createSearchbar();
        if (this.searchbar)
            this.add(this.searchbar);

        let loadStartedId = Application.documentManager.connect('load-started', Lang.bind(this,
            function() {
                this._handleEvent = true;
            }));

        let loadErrorId = Application.documentManager.connect('load-error',
            Lang.bind(this, this._onLoadErrorOrPassword));
        let passwordNeededId = Application.documentManager.connect('password-needed',
            Lang.bind(this, this._onLoadErrorOrPassword));

        this.connect('destroy', Lang.bind(this,
            function() {
                Application.documentManager.disconnect(loadStartedId);
                Application.documentManager.disconnect(loadErrorId);
                Application.documentManager.disconnect(passwordNeededId);
            }));
    },

    createSearchbar: function() {
        return null;
    },

    _onLoadErrorOrPassword: function() {
        this._handleEvent = false;
    },

    handleEvent: function(event) {
        if (!this._handleEvent)
            return false;

        let res = this.searchbar.handleEvent(event);
        return res;
    },

    addSearchButton: function(actionName) {
        let searchButton = new Gtk.ToggleButton({ image: new Gtk.Image ({ icon_name: 'edit-find-symbolic' }),
                                                  tooltip_text: Gettext.pgettext("toolbar button tooltip", "Search"),
                                                  action_name: actionName,
                                                  visible: true });
        this.toolbar.pack_end(searchButton);
        return searchButton;
    },

    addBackButton: function() {
        let backButton = new Gtk.Button({ image: new Gtk.Image({ icon_name: 'go-previous-symbolic' }),
                                          tooltip_text: _("Back"),
                                          action_name: 'view.go-back' });
        this.toolbar.pack_start(backButton);
        return backButton;
    }
});
