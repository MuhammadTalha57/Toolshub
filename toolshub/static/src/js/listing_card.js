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
        if (this.props.type === 'rentListing') {
            return this.props.listing.owner_id === this.props.currentUserId;
        }
        else if(this.props.type === 'rentedTool') {
            return false;
        } else if(this.props.type === 'groupBuy') {
            return this.props.listing.initiator_id === this.props.currentUserId;
        }
      
    }

    get isActive() {
        if(this.props.type === 'rentedTool') {
            return this.props.tool.is_active;
        }
        else if(this.props.type === 'rentListing') {
            return this.props.listing.is_active;
        } else if(this.props.type === 'rentedOutTool') {
            return this.props.tool.is_active;
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
        if (this.props.type === 'rentListing') {
            return this.props.listing.available_users - this.props.listing.subscribed_users;
        } else if(this.props.type === 'groupBuy') {
            return this.props.listing.total_required_users - this.props.listing.subscribed_users;
        }
    }

    get isFull() {
        if(this.props.type === 'rentListing') {
            return  !this.props.listing.unlimited_users && this.props.listing.available_users <= 0;
        }
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
        if(this.props.type === 'rentListing') {
            this.props.onView(this.props.listing);
        }
        else if(this.props.type === 'rentedTool') {
            this.props.onView(this.props.tool);
        } else if(this.props.type === 'rentedOutTool') {
            this.props.onView(this.props.tool);
        }
    }

    handleAction() {
        if(this.props.type === 'rentListing') {
            if (!this.isOwnListing && !this.isFull) {
                this.props.onAction(this.props.listing);
            }
        }
        else if(this.props.type === 'rentedTool') {
            this.props.onAction(this.props.tool);
        } else if(this.props.type === 'rentedOutTool') {
            this.props.onAction(this.props.tool);
        }
    }

    getActionLabel() {
        if(this.props.type === 'rentListing') {
            if (this.isOwnListing) {
                return 'Your Listing';
            }
            if (this.isFull) {
                return 'Full';
            }
            return "Rent Now";

        }
        else if(this.props.type === 'rentedTool') {
            return "View Credentials";
        }
        else if(this.props.type === 'rentedOutTool') {
            return "View Credentials";
        }
        return "Join Group";
    }

    handleToggleIsActive() {
        if(this.props.type === 'rentListing') {
            this.props.listing.is_active = !this.props.listing.is_active
            this.props.onToggleIsActive(this.props.listing);
        }
    }

}

registry.category("public_components").add("toolshub.ListingCard", ListingCard);