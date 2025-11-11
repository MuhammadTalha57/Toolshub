/** @odoo-module **/

import { Component, useState } from "@odoo/owl";

export class ThemeToggle extends Component {
    static template = "toolshub.ThemeToggle";

    setup() {
        this.state = useState({
            isDark: localStorage.getItem('theme') === 'dark'
        });

        // Apply initial theme
        this.applyTheme();
    }

    toggleTheme() {
        this.state.isDark = !this.state.isDark;
        this.applyTheme();
    }

    applyTheme() {
        // Apply user's system preference as default on first load
        if (localStorage.getItem('theme') === null) {
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            localStorage.setItem('theme', prefersDark ? 'dark' : 'light');
        }
        else {
            const theme = this.state.isDark ? 'dark' : 'light';
            localStorage.setItem('theme', theme);
        }
        document.documentElement.setAttribute('data-theme', localStorage.getItem('theme'));
    }
}

