/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
// import { session } from "@web/session";
import { rpc } from "@web/core/network/rpc";
import { Login } from "./login";
import { Dashboard } from "./dashboard";
import { Navbar } from "./navbar";
import { RentListings } from "./rent_listings";

export class ToolshubApp extends Component {
    static template = "toolshub.ToolshubApp";
    static components = {
        Login,
        Dashboard,
        Navbar,
        RentListings
    };

    setup() {
        this.state = useState({
            currentPage: 'rent',
            isAuthenticated: false,
            user: null
        });

        onWillStart(async () => {
            await this.checkUserSession();
        });
    }

    async checkUserSession() {
        try {
            const session = await rpc("/web/session/get_session_info");
            console.log("=== Checking User Session ===");
            console.log("Session UID:", session.uid);
            console.log("Session name:", session.name);
            
            // Check if user is logged in
            // session.uid will be false or null if not logged in
            // session.uid will be a number (user id) if logged in
            if (session.uid && typeof session.uid === 'number') {
                console.log("✓ User already logged in from session");
                console.log("Full session info:", session);
                
                this.state.isAuthenticated = true;
                this.state.user = {
                    id: session.uid,
                    name: session.name,
                    username: session.username,
                    email: session.user_context?.email || session.username,
                    partner_id: session.partner_id,
                    is_admin: session.is_admin || false,
                    is_system: session.is_system || false
                };
                
                this.state.currentPage = 'rent';
            } else {
                console.log("✗ No active session - user not logged in");
                this.state.isAuthenticated = false;
                this.state.user = null;
                this.state.currentPage = 'rent';
            }
            
        } catch (error) {

            if(error.message !== "Session expired") {
                console.error("Session check error:", error);
            }
            this.state.isAuthenticated = false;
            this.state.user = null;
        }
    }

    handleLoginSuccess(user) {
        console.log("=== HANDLING LOGIN SUCCESS ===");
        
        this.state.isAuthenticated = true;
        this.state.user = user;
        this.state.currentPage = 'rent';

    }

    async handleLogout() {
        try {
            console.log("=== Logging out ===");
            
            // Use Odoo's official logout endpoint
            await rpc('/web/session/destroy');
            console.log("✓ Successfully logged out");
        
            // Reload page to clear all session data
            window.location.reload();
            
        } catch (error) {
            console.error("Logout Error:", error);
            
            // Even if API fails, still clear local state and reload
            this.state.isAuthenticated = false;
            this.state.user = null;
            this.state.currentPage = 'rent';
            window.location.reload();
        }
    }

    handleNavigate(page) {
        this.state.currentPage = page;
    }

    get currentComponent() {
        switch (this.state.currentPage) {
            case 'rent':
                return 'RentListings';
            case 'groupbuy':
                return 'GroupBuyListings';
            case 'addtool':
                return 'AddTool';
            default:
                return 'RentListings';
        }
    }
}

registry.category("public_components").add("toolshub.ToolshubApp", ToolshubApp);