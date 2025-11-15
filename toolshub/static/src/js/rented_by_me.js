/** @odoo-module **/

import { Component, useState, onMounted} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { ListingCard } from "./listing_card";
import { registry } from "@web/core/registry";

export class RentedByMe extends Component {
    static template = "toolshub.RentedByMe";
    static components = { ListingCard };

    setup() {
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            rentedTools: [],
            showDetailsModal: false,
            showCredentialsModal: false,
            selectedListing: null,
            selectedTool: null,
        });

        onMounted(() => {
            this.loadRentedTools();
        });
    }

    async loadRentedTools() {
        this.state.loading = true;
        try {

            const rentedToolsResult = await rpc("/toolshub/api/getRentedTools")

            if(rentedToolsResult.success) {
                this.state.rentedTools = rentedToolsResult.data.rented_tools;
            }
            else {
                this.notification.add(rentedToolsResult.data.message, {type: 'danger', title: 'Error'});
            }
            
        } catch (error) {
            this.notification.add("Unexpected Error Occured while loading Rented Tools", {type: 'danger', title: 'Error'});
            console.error('Error loading rented tools data:', error);
        } finally {
            this.state.loading = false;
        }
    }

    closeDetailsModal() {
        this.state.showDetailsModal = false;
        this.state.selectedListing = null;
    }

    closeCredentialsModal() {
        this.state.showCredentialsModal = false;
        this.state.selectedTool = null;
    }

    viewListing(listing) {
        this.state.selectedListing = listing;
        this.state.showDetailsModal = true;
    }

    viewCredentials(tool) {
        this.state.selectedTool = tool;
        this.state.showCredentialsModal = true;
    }

}

registry.category("public_components").add("toolshub.RentedByMe", RentedByMe);