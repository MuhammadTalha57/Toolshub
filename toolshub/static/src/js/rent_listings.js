/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
// import { api } from "../services/api_service";
import { rpc } from "@web/core/network/rpc";
import { ListingCard } from "./listing_card";
import { useService } from "@web/core/utils/hooks";

export class RentListings extends Component {
    static template = "toolshub.RentListings";
    static components = { ListingCard };
    static props = {
        user: { type: Object, optional: true }
    };

    setup() {

        this.notification = useService("notification");

        this.state = useState({
            listings: [],
            tools: [],
            plans: [],
            loading: true,
            showCreateModal: false,
            showDetailsModal: false,
            selectedListing: null,
            creating: false,
            showConnectIDModal: false,
            connectAccountID: '',
            validatingConnectAccountID: false,
            newListing: {
                tool_id: '',
                plan_id: '',
                price: 0,
                total_users: 1,
                unlimited_users: false
            }
        });

        onMounted(() => {
            this.loadRentListings();
            this.handleStripeRedirect();
        });
    }

    handleStripeRedirect() {
        const urlParams = new URLSearchParams(window.location.search);
        const status = urlParams.get("status");

        if (status === "success") {
            this.notification.add("Payment successful. Thank you!", {
                type: "success",
                title: "Payment Success",
            });
        } else if (status === "cancelled") {
            this.notification.add("Payment was cancelled.", {
                type: "warning",
                title: "Payment Cancelled",
            });
        }
}

    async loadRentListings() {
        this.state.loading = true;
        try {

            const listingResult = await rpc("/toolshub/api/getRentListings")

            console.log("Rent Listings Got: ", listingResult)

            if(listingResult.success) {
                this.state.listings = listingResult.data
            }

        } catch (error) {
            console.error('Error loading listings data:', error);
        } finally {
            this.state.loading = false;
        }
    }

    async loadTools() {
        // this.state.loading = true;
        try {

            const toolsResult = await rpc("/toolshub/api/getTools")

            console.log("Tools Got: ", toolsResult)

            if(toolsResult.success) {
                this.state.tools = toolsResult.data
            }

        } catch (error) {
            console.error('Error loading tools data:', error);
        } finally {
            // this.state.loading = false;
        }
    }

    get selectedTool() {
        return this.state.tools.find(t => t.id == this.state.newListing.tool_id);
    }


    get availablePlans() {
        return this.selectedTool?.plan_ids || [];
    }

    openCreateModal() {
        if(!this.props.user.stripe_connect_account_id) {
            this.state.showConnectIDModal = true;
        }
        else {
            this.loadTools();
            this.state.showCreateModal = true;
        }
    }

    closeCreateModal() {
        this.state.showCreateModal = false;
        this.resetForm();
    }

    closeConnectIDModal() {
        this.state.showConnectIDModal = false;
        this.state.connectAccountID = ''
    }

    async handleConnectIDSubmit(ev) {
        ev.preventDefault();

        this.state.validatingConnectAccountID = true;
        const connect_id = this.state.connectAccountID;

        try {
            const validationResult = await rpc("/toolshub/validateConnectAccount", {connect_id});

            if(validationResult.success) {
                // Valid Account
                this.notification.add(validationResult.data.message, {
                type: "success",
                title: "Validated Successfully!"
                });
                this.closeConnectIDModal();
                this.props.user.stripe_connect_account_id = connect_id

            }
            else if(!validationResult.data.error) {
                // Invalid Account
                this.notification.add(validationResult.data.message, {
                type: "warning",
                title: "Validation Failed"
            });

            }

        } catch (error) {
            console.error(error);
            this.notification.add("An unexpected error occurred. Please try again.", {
                type: "danger",
                title: "Server Error"
            });
        } finally {
            this.state.validatingConnectAccountID = false;
        }

    }

    resetForm() {
        this.state.newListing = {
            tool_id: '',
            plan_id: '',
            price: 0,
            available_users: 1,
            duration_days: 30,
            description: ''
        };
    }

    updateField(field, ev) {

        const value = ['price', 'total_users'].includes(field)
            ? parseFloat(ev.target.value) || 0
            : ev.target.value;
        this.state.newListing[field] = value;

        // Reset plan when tool changes
        if (field === 'tool_id') {
            this.state.newListing.plan_id = '';
        }
    }

    onUnlimitedUsersChange(ev) {
        this.state.newListing.unlimited_users = ev.target.checked;
        
        // Set total_users to 0 when unlimited is checked
        if (this.state.newListing.unlimited_users) {
            this.state.newListing.total_users = 0;
        } else {
            // Reset to 1 when unchecked
            this.state.newListing.total_users = 1;
        }
    }

    async handleCreateListing(ev) {
        ev.preventDefault();

        console.log("Creating Rent Listing", this.state.newListing);
        
        if (!this.state.newListing.tool_id || !this.state.newListing.plan_id) {
            this.notification.add("Please select a tool and plan", {
            type: "warning",
            title: "Missing Information"
            });
            return;
        }

        if (!this.state.newListing.price || this.state.newListing.price <= 0 || isNaN(this.state.newListing.price)) {
            this.notification.add("Please enter a valid price greater than 0", {
            type: "warning",
            title: "Invalid Price"
            });
            return;
        }

        this.state.newListing.price = Number(this.state.newListing.price);

        this.state.creating = true;

        try {
            const result = await rpc("/toolshub/api/createRentListing", this.state.newListing);
    
            if(result.success) {
                this.notification.add("Rent Listing Created Successfully!", {type: "success", title: "Listing Created"});
                this.loadRentListings();
                this.closeCreateModal();
            }
            else {
                this.notification.add(result.message || "Failed to create listing", {type: "danger", title: "Error", sticky: true});
            }

        } catch (error) {
            if(error.data.name === "odoo.exceptions.ValidationError") {
                this.notification.add(error.data.message, {
                    type: "danger",
                    title: "Validation Error"
                });
                return;
            }
            console.error("Error creating listing:", error.data);
            // Error notification
            this.notification.add("An unexpected error occurred. Please try again.", {
                type: "danger",
                title: "Server Error"
            });

        } finally {
            this.state.creating = false;
        }
    }

    viewListing(listing) {
        this.state.selectedListing = listing;
        this.state.showDetailsModal = true;
    }

    closeDetailsModal() {
        this.state.showDetailsModal = false;
        this.state.selectedListing = null;
    }

    async rentListing(listing) {
        if (confirm(`Rent ${listing.tool_name} - ${listing.plan_name} for $${listing.price}?`)) {
            try {
                
                console.log("PAssing listing", {listing});
                const paymentResult = await rpc("/toolshub/processRentPayment", {listing});
                if(paymentResult.success) {
                    console.log("REDIRECTING USER TO CHECKOUT SESSION");
                    window.location.href = paymentResult.data.checkout_url; // Redirect to Stripe Checkout
                }
                else {
                    this.notification.add(paymentResult.data.message, {
                    type: "danger",
                    title: "Server Error"
                    });
            }

            } catch (error) {
                console.error('Error Processing Payment:', error);
            }
        }
    }

}

registry.category("public_components").add("toolshub.RentListings", RentListings);