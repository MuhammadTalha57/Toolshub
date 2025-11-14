/** @odoo-module **/

import { Component } from "@odoo/owl";
import { ThemeToggle } from "./theme_toggle";

export class Navbar extends Component {
    static template = "toolshub.Navbar";
    static components = { ThemeToggle };
    static props = {
        currentPage: { type: String },
        onNavigate: { type: Function },
        user: { type: Object, optional: true },
        onLogout: { type: Function, optional: true }
    };

    get pages() {
        return [
            { id: 'rent', label: 'Rent Tools', icon: 'fa-store' },
            { id: 'rented-out', label: 'Rented Out', icon: 'fa-hand-holding-usd' },
            { id: 'rented-by-me', label: 'Rented by Me', icon: 'fa-shopping-bag' },
            // { id: 'groupbuy', label: 'Group Buy', icon: 'fa-users' },
            // { id: 'addtool', label: 'Add Tool', icon: 'fa-plus-circle' }
        ];
    }

    isActive(pageId) {
        return this.props.currentPage === pageId;
    }

    handleNavigate(pageId) {
        this.props.onNavigate(pageId);
    }

    handleLogout() {
        if (this.props.onLogout) {
            this.props.onLogout();
        }
    }
}