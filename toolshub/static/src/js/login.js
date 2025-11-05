/** @odoo-module **/

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";

export class Login extends Component {
    static template = "toolshub.Login";
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
                console.log("✓ Successfully Logged in");
                
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
            
            const csrfToken = this.getCSRFToken();
            
            const formData = new URLSearchParams();
            if (csrfToken) {
                formData.append('csrf_token', csrfToken);
            }
            formData.append('name', this.state.username);
            formData.append('login', this.state.email);
            formData.append('password', this.state.password);
            formData.append('confirm_password', this.state.confirmPassword);

            const response = await fetch('/web/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                credentials: 'include',
                body: formData.toString()
            });

            const text = await response.text();

            // console.log(response, text);

            if (!response.ok) {


                this.state.error = "Signup Failed";
                return;



                // console.log("=== ERROR RESPONSE ===");
                
                // // Parse HTML to extract error
                // const parser = new DOMParser();
                // const doc = parser.parseFromString(text, 'text/html');
                
                // // Try multiple selectors to find the error
                // const errorSelectors = [
                //     '.alert-danger',
                //     '.text-danger', 
                //     'div.error',
                //     'p.text-danger',
                //     'div[role="alert"]',
                //     '.o_error_detail',
                //     'h1', // Sometimes the error is in h1
                // ];
                
                // let errorMessage = null;
                // for (const selector of errorSelectors) {
                //     const element = doc.querySelector(selector);
                //     if (element) {
                //         errorMessage = element.textContent.trim();
                //         console.log(`Found error in ${selector}:`, errorMessage);
                //         if (errorMessage.length > 5) { // Valid error message
                //             break;
                //         }
                //     }
                // }

                // // Log the full HTML for debugging (you can remove this later)
                // console.log("Full HTML response:", text);

                // // Set appropriate error message
                // if (errorMessage) {
                //     this.state.error = errorMessage;
                // } else if (text.includes('not found') || text.includes('NotFound') || text.includes('404')) {
                //     this.state.error = 'Signup is not available. Please enable "Free sign up" in Settings → General Settings';
                // } else if (text.includes('werkzeug.exceptions.NotFound')) {
                //     this.state.error = 'Signup endpoint not found. Ensure auth_signup module is installed and signup is enabled.';
                // } else {
                //     this.state.error = 'Signup failed. Please contact administrator to enable signup.';
                // }
                
                // return;
            }

            // Success
            console.log("✓ Signup successful");
            // await new Promise(resolve => setTimeout(resolve, 1000));
            await this.handleLogin();
            
        } catch (error) {
            console.error("Signup Error:", error);
            this.state.error = 'An error occurred during signup.';
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