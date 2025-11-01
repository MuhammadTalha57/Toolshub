/** @odoo-module **/

import { Component, useState, onWillStart } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { Login } from "./login";
// import { Navbar } from "./components/navbar";
// import { AddTool } from "./components/add_tool";
// import { RentListings } from "./components/rent_listings";
// import { GroupBuyListings } from "./components/group_buy_listings";
// import { api } from "./services/api_service";


const BASE_URL = "http://192.168.100.45:8069";

export class ToolshubApp extends Component {
    static template = "toolshub.ToolshubApp";
    static components = {
        Login,
        // Navbar,
        // AddTool,
        // RentListings,
        // GroupBuyListings
    };

    setup() {
        this.state = useState({
            currentPage: 'rent',
            isAuthenticated: false,
            user: null
        });

        onWillStart(async () => {
            // Check if user is already logged in

            // try {

            //     const response = await fetch(`${BASE_URL}/api/auth/check`, {
            //         method: 'POST',
            //         headers: {
            //             'Content-Type': 'application/json',
            //         },
            //         credentials: 'include', // Important for session cookies
            //         body: JSON.stringify({
            //             jsonrpc: '2.0',
            //             method: 'call',
            //             params: {}
            //         })
            //     });
            // } catch (error) {
            //     console.log("API Error")
            //     this.state.error = "Can't Reach API"
            //     return;
            // } 
            
            // const data = await response.json();

            // if(data.success) {
            //     this.state.isAuthenticated = true;
            //     this.state.user = data.user;
            // }

            // const user = api.getCurrentUser();
            // if (user) {
            //     this.state.isAuthenticated = true;
            //     this.state.user = user;
            // }
        });
    }

    handleLoginSuccess(user) {
        this.state.isAuthenticated = true;
        this.state.user = user;
        this.state.currentPage = 'rent';
    }

    handleLogout() {
        api.logout();
        this.state.isAuthenticated = false;
        this.state.user = null;
        this.state.currentPage = 'rent';
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

// Register the main app as a client action
// registry.category("actions").add("toolshub_main_app", ToolshubApp);
registry.category("public_components").add("toolshub.ToolshubApp", ToolshubApp);