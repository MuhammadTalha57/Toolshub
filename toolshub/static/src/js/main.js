import { whenReady, mount} from "@odoo/owl";
import { mountComponent } from "@web/env";
import { Homepage } from "./homepage";

const config = {
    dev: true,
    name: "Owl Tutorial" 
};

// Mount the Playground component when the document.body is ready
// whenReady(() => mountComponent(Homepage, document.body, config));
