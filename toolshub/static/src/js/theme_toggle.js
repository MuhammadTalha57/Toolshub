/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class ThemeToggle extends Component {
    static template = "toolshub.ThemeToggle";

    setup() {
        this.state = useState({
            isDark: localStorage.getItem('theme') === 'dark' || false
        });

        // Apply initial theme
        this.applyTheme();
    }

    toggleTheme() {
        this.state.isDark = !this.state.isDark;
        this.applyTheme();
    }

    applyTheme() {
        if (this.state.isDark) {
            document.documentElement.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
            localStorage.setItem('theme', 'light');
        }
    }
}