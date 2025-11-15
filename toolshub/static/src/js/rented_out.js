/** @odoo-module **/

import { Component, useState, onMounted} from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { ListingCard } from "./listing_card";
import { registry } from "@web/core/registry";

export class RentedOut extends Component {
    static template = "toolshub.RentedOut";
    static components = { ListingCard };

    setup() {
        this.notification = useService("notification");

        this.state = useState({
            loading: true,
            rentedOutTools: [],
            showDetailsModal: false,
            showCredentialsModal: false,
            selectedListing: null,
            selectedTool: null,
            login: null,
            password: null,
        });

        onMounted(() => {
            this.loadRentedOutTools();
        });
    }

    async loadRentedOutTools() {
        this.state.loading = true;
        try {

            const rentedOutToolsResult = await rpc("/toolshub/api/getRentedOutTools")

            if(rentedOutToolsResult.success) {
                this.state.rentedOutTools = rentedOutToolsResult.data.rented_out_tools;
            }
            else {
                this.notification.add(rentedOutToolsResult.data.message, {type: 'danger', title: 'Error'});
            }
            
        } catch (error) {
            this.notification.add("Unexpected Error Occured while loading Rented Out Tools", {type: 'danger', title: 'Error'});
            console.error('Error loading rented out tools data:', error);
        } finally {
            this.state.loading = false;
        }
    }

    closeDetailsModal() {
        this.state.showDetailsModal = false;
        this.state.selectedListing = null;
        this.state.selectedTool = null;
    }

    closeCredentialsModal() {
        this.state.showCredentialsModal = false;
        this.state.selectedTool = null;
    }

    viewListing(tool) {
        this.state.selectedTool = tool;
        this.state.selectedListing = tool.listing;
        this.state.showDetailsModal = true;
    }

    viewCredentials(tool) {
        this.state.selectedTool = tool;
        this.state.login = tool.login;
        this.state.password = tool.password;
        this.state.showCredentialsModal = true;

    }


    async handleCredentialsSubmit(ev) {
        ev.preventDefault();

        try {
            const result = await rpc("/toolshub/api/updateRentedToolCredentials", {'rented_tool_id': this.state.selectedTool.id, 'login': this.state.login, 'password': this.state.password});

            if (result.success) {
                this.notification.add(result.data.message, {
                    type: "success",
                    title: "Credentials Updated"
                });

                // Update the listing in state
                const rentedOutToolIndex = this.state.rentedOutTools.findIndex(tool => tool.id === this.state.selectedTool.id);
                if (rentedOutToolIndex !== -1) {
                    this.state.rentedOutTools[rentedOutToolIndex].login = result.data.login;
                    this.state.rentedOutTools[rentedOutToolIndex].password = result.data.password;
                }
            } else {
                this.notification.add(result.data.message, {
                    type: "danger",
                    title: "Error"
                });
            }

        } catch (error) {
            console.error('Error while updating credentials:', error);
            this.notification.add("Unexpected Error Occurred while updating credentials", {
                type: "danger",
                title: "Error"
            });
        } finally {
            this.closeCredentialsModal();
        }

    }

}

registry.category("public_components").add("toolshub.RentedOut", RentedOut);