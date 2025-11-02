/** @odoo-module **/

const BASE_URL = "http://192.168.100.45:8069";

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry"
// import { api } from "../services/api_service";

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

            const response = await fetch(`${BASE_URL}/api/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Important for session cookies
                body: JSON.stringify({
                    jsonrpc: '2.0',
                    method: 'call',
                    params: {
                        email: this.state.email,
                        password: this.state.password
                    }
                })
            });

            const data = await response.json();
            const result = data.result;

            if(result.success) {
                console.log("Successfully Logged in");
                console.log(result);
                this.props.onLoginSuccess(result.user);
            }
            else {
                this.state.error = result.message;
            }
        } catch (error) {
            console.log("API Error")
            this.state.error = error;
            return;
        } finally {
            this.state.loading = false;
        }
        


        


        // try {
        //     const result = await api.login(this.state.username, this.state.password);
        //     if (result.success) {
        //         this.props.onLoginSuccess(result.user);
        //     } else {
        //         this.state.error = 'Invalid credentials';
        //     }
        // } catch (error) {
        //     this.state.error = 'An error occurred. Please try again.';
        // } finally {
        //     this.state.loading = false;
        // }
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

            const response = await fetch(`${BASE_URL}/api/auth/signup`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'include', // Important for session cookies
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
            const result = data.result;

            if(result.success) {
                console.log("Successfully Signed up");
                console.log(result);

                // Auto Login after signup
                this.handleLogin();
            }
            
            this.state.error = data.result.message;

        } catch (error) {
            console.log("API Error")
            this.state.error = "Can't Reach API"
            return;
        } finally {
            this.state.loading = false;
        }
        


        

        // try {
        //     const result = await api.signup({
        //         username: this.state.username,
        //         email: this.state.email,
        //         password: this.state.password
        //     });
            
        //     if (result.success) {
        //         // Auto login after signup
        //         const loginResult = await api.login(this.state.username, this.state.password);
        //         if (loginResult.success) {
        //             this.props.onLoginSuccess(loginResult.user);
        //         }
        //     } else {
        //         this.state.error = 'Signup failed. Please try again.';
        //     }
        // } catch (error) {
        //     this.state.error = 'An error occurred. Please try again.';
        // } finally {
        //     this.state.loading = false;
        // }
    }

    updateField(field, ev) {
        this.state[field] = ev.target.value;
    }
}

registry.category("public_components").add("toolshub.Login", Login);
