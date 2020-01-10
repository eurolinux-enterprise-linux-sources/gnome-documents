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

const Gd = imports.gi.Gd;
const Gdk = imports.gi.Gdk;
const GLib = imports.gi.GLib;
const Gtk = imports.gi.Gtk;
const Tracker = imports.gi.Tracker;
const _ = imports.gettext.gettext;

const Lang = imports.lang;
const Mainloop = imports.mainloop;
const Signals = imports.signals;

const Application = imports.application;
const Manager = imports.manager;
const Tweener = imports.tweener.tweener;
const Utils = imports.utils;

const Searchbar = new Lang.Class({
    Name: 'Searchbar',

    _init: function() {
        this._searchTypeId = 0;
        this._searchMatchId = 0;
        this.searchChangeBlocked = false;

        this._in = false;

        this.widget = new Gtk.Revealer();

        let toolbar = new Gtk.Toolbar();
        toolbar.get_style_context().add_class("search-bar");
        this.widget.add(toolbar);

        // subclasses will create this._searchEntry and this._searchContainer
        // GtkWidgets
        this.createSearchWidgets();

        let item = new Gtk.ToolItem();
        item.set_expand(true);
        item.add(this._searchContainer);
        toolbar.insert(item, 0);

        this._searchEntry.connect('search-changed', Lang.bind(this,
            function() {
                if (this.searchChangeBlocked)
                    return;

                this.entryChanged();
            }));

        // connect to the search action state for visibility
        let searchStateId = Application.application.connect('action-state-changed::search',
            Lang.bind(this, this._onActionStateChanged));
        this._onActionStateChanged(Application.application, 'search', Application.application.get_action_state('search'));

        this.widget.connect('destroy', Lang.bind(this,
            function() {
                Application.application.disconnect(searchStateId);
                Application.application.change_action_state('search', GLib.Variant.new('b', false));
            }));

        this.widget.show_all();
    },

    _onActionStateChanged: function(source, actionName, state) {
        if (state.get_boolean())
            this.show();
        else
            this.hide();
    },

    createSearchWidgets: function() {
        log('Error: Searchbar implementations must override createSearchWidgets');
    },

    entryChanged: function() {
        log('Error: Searchbar implementations must override entryChanged');
    },

    destroy: function() {
        this.widget.destroy();
    },

    _isEscapeEvent: function(event) {
        let keyval = event.get_keyval()[1];
        return (keyval == Gdk.KEY_Escape);
    },

    _isKeynavEvent: function(event) {
        let keyval = event.get_keyval()[1];
        let state = event.get_state()[1];

        if (keyval == Gdk.KEY_Up ||
            keyval == Gdk.KEY_KP_Up ||
            keyval == Gdk.KEY_Down ||
            keyval == Gdk.KEY_KP_Down ||
            keyval == Gdk.KEY_Left ||
            keyval == Gdk.KEY_KP_Left ||
            keyval == Gdk.KEY_Right ||
            keyval == Gdk.KEY_KP_Right ||
            keyval == Gdk.KEY_Home ||
            keyval == Gdk.KEY_KP_Home ||
            keyval == Gdk.KEY_End ||
            keyval == Gdk.KEY_KP_End ||
            keyval == Gdk.KEY_Page_Up ||
            keyval == Gdk.KEY_KP_Page_Up ||
            keyval == Gdk.KEY_Page_Down ||
            keyval == Gdk.KEY_KP_Page_Down ||
            (state & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.MOD1_MASK) != 0))
            return true;

        return false;
    },

    _isSpaceEvent: function(event) {
        let keyval = event.get_keyval()[1];
        return (keyval == Gdk.KEY_space);
    },

    _isTabEvent: function(event) {
        let keyval = event.get_keyval()[1];
        return (keyval == Gdk.KEY_Tab || keyval == Gdk.KEY_KP_Tab);
    },

    handleEvent: function(event) {
        // Skip if the search bar is shown and the focus is elsewhere
        if (this._in && !this._searchEntry.is_focus)
            return false;

        let isEscape = this._isEscapeEvent(event);
        let isKeynav = this._isKeynavEvent(event);
        let isTab = this._isTabEvent(event);
        let isSpace = this._isSpaceEvent(event);

        // Skip these if the search bar is hidden
        if (!this._in && (isEscape || isKeynav || isTab || isSpace))
            return false;

        // At this point, either the search bar is hidden and the event
        // is neither escape nor keynav nor space; or the search bar is
        // shown and has the focus.

        let keyval = event.get_keyval()[1];
        if (isEscape) {
            Application.application.change_action_state('search', GLib.Variant.new('b', false));
            return true;
        } else if (keyval == Gdk.KEY_Return) {
            this.emit('activate-result');
            return true;
        }

        if (!this._searchEntry.get_realized())
            this._searchEntry.realize();

        // Since we can have keynav or space only when the search bar
        // is shown, we want to handle it. Otherwise it will hinder
        // text input. However, we don't want to handle tabs so that
        // focus can be shifted to other widgets.
        let handled = isKeynav || isSpace;

        let preeditChanged = false;
        let preeditChangedId =
            this._searchEntry.connect('preedit-changed', Lang.bind(this,
                function() {
                    preeditChanged = true;
                }));

        let oldText = this._searchEntry.get_text();
        let res = this._searchEntry.event(event);
        let newText = this._searchEntry.get_text();

        this._searchEntry.disconnect(preeditChangedId);

        if (((res && (newText != oldText)) || preeditChanged)) {
            handled = true;

            if (!this._in)
                Application.application.change_action_state('search', GLib.Variant.new('b', true));
        }

        return handled;
    },

    show: function() {
        let eventDevice = Gtk.get_current_event_device();
        this.widget.set_reveal_child(true);
        this._in = true;

        if (eventDevice)
            Gd.entry_focus_hack(this._searchEntry, eventDevice);
    },

    hide: function() {
        this._in = false;
        this.widget.set_reveal_child(false);
        // clear all the search properties when hiding the entry
        this._searchEntry.set_text('');
    }
});
Signals.addSignalMethods(Searchbar.prototype);

const Dropdown = new Lang.Class({
    Name: 'Dropdown',
    Extends: Gtk.Popover,

    _init: function(relativeTo) {
        this.parent({ relative_to: relativeTo, position: Gtk.PositionType.BOTTOM });

        let grid = new Gtk.Grid({ orientation: Gtk.Orientation.HORIZONTAL,
                                  row_homogeneous: true });
        this.add(grid);

        [Application.sourceManager,
         Application.searchTypeManager,
         Application.searchMatchManager].forEach(Lang.bind(this, function(manager) {
             let model = new Manager.BaseModel(manager);

             // HACK: see https://bugzilla.gnome.org/show_bug.cgi?id=733977
             let popover = new Gtk.Popover();
             popover.bind_model(model.model, 'app');
             let w = popover.get_child();
             w.reparent(grid);
             w.valign = Gtk.Align.START;
             w.vexpand = true;
             popover.destroy();
         }));
    }
});

const OverviewSearchbar = new Lang.Class({
    Name: 'OverviewSearchbar',
    Extends: Searchbar,

    _init: function() {
        this._selectAll = Application.application.lookup_action('select-all');

        this.parent();

        this._sourcesId = Application.sourceManager.connect('active-changed',
            Lang.bind(this, this._onActiveSourceChanged));
        this._searchTypeId = Application.searchTypeManager.connect('active-changed',
            Lang.bind(this, this._onActiveTypeChanged));
        this._searchMatchId = Application.searchMatchManager.connect('active-changed',
            Lang.bind(this, this._onActiveMatchChanged));
        this._collectionId = Application.collectionManager.connect('active-changed',
            Lang.bind(this, this._onActiveCollectionChanged));

        this._onActiveSourceChanged();
        this._onActiveTypeChanged();
        this._onActiveMatchChanged();

        this._searchEntry.set_text(Application.searchController.getString());
    },

    createSearchWidgets: function() {
        // create the search entry
        this._searchEntry = new Gd.TaggedEntry({ width_request: 500 });
        this._searchEntry.connect('tag-clicked',
            Lang.bind(this, this._onTagClicked));
        this._searchEntry.connect('tag-button-clicked',
            Lang.bind(this, this._onTagButtonClicked));

        this._sourceTag = new Gd.TaggedEntryTag();
        this._typeTag = new Gd.TaggedEntryTag();
        this._matchTag = new Gd.TaggedEntryTag();

        // connect to search string changes in the controller
        this._searchChangedId = Application.searchController.connect('search-string-changed',
            Lang.bind(this, this._onSearchStringChanged));

        this._searchEntry.connect('destroy', Lang.bind(this,
            function() {
                this._dropdown.hide();
                Application.searchController.disconnect(this._searchChangedId);
            }));

        // create the dropdown button
        this._dropdownButton = new Gtk.ToggleButton(
            { child: new Gtk.Arrow({ arrow_type: Gtk.ArrowType.DOWN }) });
        this._dropdownButton.get_style_context().add_class('raised');
        this._dropdownButton.get_style_context().add_class('image-button');
        this._dropdownButton.connect('toggled', Lang.bind(this,
            function() {
                let active = this._dropdownButton.get_active();
                if(active)
                    this._dropdown.show_all();
            }));

        this._dropdown = new Dropdown(this._dropdownButton);
        this._dropdown.connect('closed', Lang.bind(this,
            function() {
                this._dropdownButton.set_active(false);
            }));

        this._searchContainer = new Gtk.Box({ orientation: Gtk.Orientation.HORIZONTAL,
                                              halign: Gtk.Align.CENTER });
        this._searchContainer.get_style_context().add_class('linked');

        this._searchContainer.add(this._searchEntry);
        this._searchContainer.add(this._dropdownButton);
        this._searchContainer.show_all();
    },

    entryChanged: function() {
        let currentText = this._searchEntry.get_text();

        Application.searchController.disconnect(this._searchChangedId);
        Application.searchController.setString(currentText);

        // connect to search string changes in the controller
        this._searchChangedId = Application.searchController.connect('search-string-changed',
            Lang.bind(this, this._onSearchStringChanged));
    },

    _onSearchStringChanged: function(controller, string) {
        this._searchEntry.set_text(string);
    },

    _onActiveCollectionChanged: function() {
        let searchType = Application.searchTypeManager.getActiveItem();

        if (Application.searchController.getString() != '' ||
            searchType.id != 'all') {
            Application.searchTypeManager.setActiveItemById('all');
            this._searchEntry.set_text('');
        }
    },

    _onActiveChangedCommon: function(id, manager, tag) {
        let item = manager.getActiveItem();

        if (item.id == 'all') {
            this._searchEntry.remove_tag(tag);
        } else {
            tag.set_label(item.name);
            this._searchEntry.add_tag(tag);
        }

        let eventDevice = Gtk.get_current_event_device();
        if (eventDevice)
            Gd.entry_focus_hack(this._searchEntry, eventDevice);
    },

    _onActiveSourceChanged: function() {
        this._onActiveChangedCommon('source', Application.sourceManager, this._sourceTag);
    },

    _onActiveTypeChanged: function() {
        this._onActiveChangedCommon('type', Application.searchTypeManager, this._typeTag);
    },

    _onActiveMatchChanged: function() {
        this._onActiveChangedCommon('match', Application.searchMatchManager, this._matchTag);
    },

    _onTagButtonClicked: function(entry, tag) {
        let manager = null;

        if (tag == this._matchTag) {
            manager = Application.searchMatchManager;
        } else if (tag == this._typeTag) {
            manager = Application.searchTypeManager;
        } else if (tag == this._sourceTag) {
            manager = Application.sourceManager;
        }

        if (manager) {
            manager.setActiveItemById('all');
        }
    },

    _onTagClicked: function() {
        this._dropdownButton.set_active(true);
    },

    destroy: function() {
        if (this._sourcesId != 0) {
            Application.sourceManager.disconnect(this._sourcesId);
            this._sourcesId = 0;
        }

        if (this._searchTypeId != 0) {
            Application.searchTypeManager.disconnect(this._searchTypeId);
            this._searchTypeId = 0;
        }

        if (this._searchMatchId != 0) {
            Application.searchMatchManager.disconnect(this._searchMatchId);
            this._searchMatchId = 0;
        }

        if (this._collectionId != 0) {
            Application.collectionManager.disconnect(this._collectionId);
            this._collectionId = 0;
        }

        this.parent();
    },

    show: function() {
        this._selectAll.enabled = false;
        this.parent();
    },

    hide: function() {
        this._dropdownButton.set_active(false);
        this._selectAll.enabled = true;

        Application.searchTypeManager.setActiveItemById('all');
        Application.searchMatchManager.setActiveItemById('all');
        Application.sourceManager.setActiveItemById('all');

        this.parent();
    }
});
