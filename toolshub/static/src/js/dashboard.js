/** @odoo-module **/

const BASE_URL = "http://192.168.100.45:8069";

import { Component, useState } from "@odoo/owl";
import { registry } from "@web/core/registry"
// import { api } from "../services/api_service";

export class Dashboard extends Component {
    static template = "toolshub.Dashboard";
    static props = {
        user: {type: Object}
    };
    
}

registry.category("public_components").add("toolshub.Dashboard", Dashboard);
