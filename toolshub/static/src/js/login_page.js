import { Component } from "@odoo/owl";
import { registry } from "@web/core/registry"

export class LoginPage extends Component {
    static template = "login_page";
}

// LoginPage.template = "toolshub.login_page_template"
registry.category("public_components").add("toolshub.login_page", LoginPage);