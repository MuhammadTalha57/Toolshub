/** @odoo-module **/

import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";

export class ListingCard extends Component {
    static template = "toolshub.ListingCard";
    static props = {
        listing: { type: Object},
        tool: { type: Object, optional: true},
        type: { type: String }, // 'rent' or 'groupbuy'
        currentUserId: { type: Number, optional: true },
        onView: { type: Function },
        onAction: { type: Function },
        onToggleIsActive: { type: Function, optional: true}
    };

    get isOwnListing() {
        if (this.props.type === 'rent') {
            return this.props.listing.owner_id === this.props.currentUserId;
        }
        else if(this.props.type === 'rentedtool') {
            return false;
        } else {
            return this.props.listing.initiator_id === this.props.currentUserId;
        }
      
    }

    get isActive() {
        if(this.props.type === 'rentedtool') {
            return true;
        }
        if(this.props.type === 'rent') {
            return this.props.listing.is_active;
        }
    }

    get progress() {
        if (this.props.type === 'groupbuy') {
            return Math.min(
                (this.props.listing.subscribed_users / this.props.listing.total_required_users) * 100,
                100
            );
        }
        return 0;
    }

    get availableSlots() {
        if (this.props.type === 'rent') {
            return this.props.listing.available_users - this.props.listing.subscribed_users;
        } else {
            return this.props.listing.total_required_users - this.props.listing.subscribed_users;
        }
    }

    get isFull() {
        return this.availableSlots <= 0;
    }

    get daysLeft() {
        if (this.props.type === 'groupbuy' && this.props.listing.deadline) {
            const deadline = new Date(this.props.listing.deadline);
            const today = new Date();
            const diffTime = deadline - today;
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            return diffDays > 0 ? diffDays : 0;
        }
        return null;
    }

    handleView() {
        this.props.onView(this.props.listing);
    }

    handleAction() {
        if (!this.isOwnListing && !this.isFull) {
            this.props.onAction(this.props.listing);
        }
    }

    getActionLabel() {
        if (this.isOwnListing) {
            return 'Your Listing';
        }
        if (this.isFull) {
            return 'Full';
        }
        if(this.props.type === 'rentedtool') {
            return "View Credentials";
        }
        return this.props.type === 'rent' ? 'Rent Now' : 'Join Group';
    }

    handleToggleIsActive() {
        this.props.listing.is_active = !this.props.listing.is_active
        this.props.onToggleIsActive(this.props.listing);
    }

}

registry.category("public_components").add("toolshub.ListingCard", ListingCard);