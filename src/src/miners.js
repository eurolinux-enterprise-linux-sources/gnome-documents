/*
 * Copyright (c) 2012, 2013 Red Hat, Inc.
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
 * Authors:
 *    Cosimo Cecchi <cosimoc@redhat.com>
 *    Debarshi Ray <debarshir@gnome.org>
 */

const Gio = imports.gi.Gio;
const GLib = imports.gi.GLib;

const MinerIface = '<node> \
<interface name="org.gnome.OnlineMiners.Miner"> \
    <method name="RefreshDB"> \
        <arg name="index_types" type="as" direction="in"/> \
    </method> \
    <property name="DisplayName" type="s" access="read"/> \
</interface> \
</node>';

var MinerProxy = Gio.DBusProxy.makeProxyWrapper(MinerIface);

function _makeMinerProxy(iface, path, callback) {
    let miner = new MinerProxy(Gio.DBus.session, iface, path, callback);
    miner.set_default_timeout(GLib.MAXINT32);
    return miner;
}

function GDataMiner(callback) {
    return _makeMinerProxy('org.gnome.OnlineMiners.GData',
                           '/org/gnome/OnlineMiners/GData',
                           callback);
}

function OwncloudMiner(callback) {
    return _makeMinerProxy('org.gnome.OnlineMiners.Owncloud',
                           '/org/gnome/OnlineMiners/Owncloud',
                           callback);
}

function ZpjMiner(callback) {
    return _makeMinerProxy('org.gnome.OnlineMiners.Zpj',
                           '/org/gnome/OnlineMiners/Zpj',
                           callback);
}
