/** @odoo-module **/

import { Component, useState, onMounted } from "@odoo/owl";
import { registry } from "@web/core/registry";
// import { api } from "../services/api_service";
import { rpc } from "@web/core/network/rpc";
import { ListingCard } from "./listing_card";

export class RentListings extends Component {
    static template = "toolshub.RentListings";
    static components = { ListingCard };
    static props = {
        user: { type: Object, optional: true }
    };

    setup() {
        this.state = useState({
            listings: [],
            tools: [],
            loading: true,
            showCreateModal: false,
            showDetailsModal: false,
            selectedListing: null,
            newListing: {
                tool_id: '',
                plan_id: '',
                price: 0,
                available_users: 1,
                duration_days: 30,
                description: ''
            }
        });

        onMounted(() => {
            this.loadData();
        });
    }

    async loadData() {
        this.state.loading = true;
        try {

            const listingResult = await rpc("/toolshub/getRentListings")

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

    get selectedTool() {
        return this.state.tools.find(t => t.id == this.state.newListing.tool_id);
    }

    get availablePlans() {
        return this.selectedTool?.plans || [];
    }

    openCreateModal() {
        this.state.showCreateModal = true;
    }

    closeCreateModal() {
        this.state.showCreateModal = false;
        this.resetForm();
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
        const value = ['price', 'available_users', 'duration_days'].includes(field)
            ? parseFloat(ev.target.value) || 0
            : ev.target.value;
        this.state.newListing[field] = value;

        // Reset plan when tool changes
        if (field === 'tool_id') {
            this.state.newListing.plan_id = '';
        }
    }

    async handleCreateListing(ev) {
        ev.preventDefault();

        if (!this.state.newListing.tool_id || !this.state.newListing.plan_id) {
            alert('Please select a tool and plan');
            return;
        }

        const tool = this.state.tools.find(t => t.id == this.state.newListing.tool_id);
        const plan = tool?.plans.find(p => p.id == this.state.newListing.plan_id);

        if (!tool || !plan) return;

        const listingData = {
            ...this.state.newListing,
            tool_name: tool.name,
            plan_name: plan.name,
            image_url: tool.image_url,
            owner_name: this.props.user?.name || 'You'
        };

        const result = await api.createRentListing(listingData);
        if (result.success) {
            await this.loadData();
            this.closeCreateModal();
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
            const result = await api.rentListing(listing.id);
            if (result.success) {
                alert(result.message);
                await this.loadData();
                this.closeDetailsModal();
            }
        }
    }
}

registry.category("public_components").add("toolshub.RentListings", RentListings);