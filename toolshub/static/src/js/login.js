/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { ThemeToggle } from "./theme_toggle";

export class Login extends Component {
    static template = "toolshub.Login";
    static components = {ThemeToggle};
    static props = {
        onLoginSuccess: { type: Function }
    };

    setup() {
        this.state = useState({
            isLogin: true,
            username: '',
            password: '',
            email: '',
            confirmPassword: '',
            loading: false,
            error: ''
        });
    }

    toggleMode() {
        this.state.isLogin = !this.state.isLogin;
        this.state.error = '';
        this.clearForm();
    }

    clearForm() {
        this.state.username = '';
        this.state.password = '';
        this.state.email = '';
        this.state.confirmPassword = '';
    }

    async handleSubmit(ev) {
        ev.preventDefault();
        this.state.error = '';

        if (this.state.isLogin) {
            await this.handleLogin();
        } else {
            await this.handleSignup();
        }
    }

    async handleLogin() {
        if (!this.state.email || !this.state.password) {
            this.state.error = 'Please fill in all fields';
            return;
        }

        this.state.loading = true;

        try {
            const dbName = this.getDatabaseName();
            
            console.log("=== LOGIN ATTEMPT ===");

            const response = await fetch('/web/session/authenticate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        db: dbName,
                        login: this.state.email,
                        password: this.state.password
                    }
                })
            });

            const data = await response.json();

            if (data.error) {
                console.error("RPC Error:", data.error);
                const errorMessage = data.error.data?.message || data.error.message || 'Login failed';
                this.state.error = errorMessage;
                return;
            }

            const result = data.result;

            if (result && result.uid) {
                console.log("✓ Successfully Logged in", result);
                
                const userInfo = {
                    id: result.uid,
                    name: result.name,
                    username: result.username,
                    email: this.state.email,
                    partner_id: result.partner_id,
                    is_admin: result.is_admin || false,
                    is_system: result.is_system || false
                };
                
                this.props.onLoginSuccess(userInfo);
                
            } else {
                this.state.error = 'Invalid email or password';
            }
        } catch (error) {
            console.error("Login Error:", error);
            this.state.error = 'An error occurred. Please try again.';
        } finally {
            this.state.loading = false;
        }
    }

    async handleSignup() {
        if (!this.state.username || !this.state.email || !this.state.password || !this.state.confirmPassword) {
            this.state.error = 'Please fill in all fields';
            return;
        }

        if (this.state.password !== this.state.confirmPassword) {
            this.state.error = 'Passwords do not match';
            return;
        }

        if (this.state.password.length < 6) {
            this.state.error = 'Password must be at least 6 characters';
            return;
        }

        this.state.loading = true;

        try {
            console.log("=== SIGNUP ATTEMPT ===");
            
            const response = await fetch('/toolshub/api/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include',
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        name: this.state.username,
                        email: this.state.email,
                        password: this.state.password
                    }
                })
            });

            const data = await response.json();

            if (data.error) {
                console.error("RPC Error:", data.error);
                const errorMessage = data.error.data?.message || data.error.message || 'Signup failed';
                this.state.error = errorMessage;
                return;
            }

            const result = data.result;

            if (result && result.success) {
                console.log("✓ Signup successful:", result.data.message);
                
                // Show success message and switch to login mode
                this.state.error = ''; // Clear any errors
                alert(result.data.message); // Show activation email message
                
                // Switch to login mode
                this.state.isLogin = true;
                this.clearForm();
                
            } else {
                this.state.error = result?.data?.message || 'Signup failed';
            }
            
        } catch (error) {
            console.error("Signup Error:", error);
            this.state.error = 'An error occurred during signup. Please try again.';
        } finally {
            this.state.loading = false;
        }
    }

    getCSRFToken() {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }

        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrf_token') {
                return decodeURIComponent(value);
            }
        }

        if (window.odoo && window.odoo.csrf_token) {
            return window.odoo.csrf_token;
        }

        return null;
    }

    getDatabaseName() {
        return 'E-Commerce-CEP';
    }

    updateField(field, ev) {
        this.state[field] = ev.target.value;
    }
}

registry.category("public_components").add("toolshub.Login", Login);