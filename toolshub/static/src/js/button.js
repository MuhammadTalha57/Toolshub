/** @odoo-module **/

import { Component, xml } from "@odoo/owl";
import { registry } from "@web/core/registry"

// Utility: build class names like cn()
// function cn(...classes) {
//     return classes.filter(Boolean).join(" ");
// }

// // Button variants and sizes
// const buttonVariants = {
//     variant: {
//         default: "bg-primary text-white hover:bg-primary-90",
//         destructive: "bg-red text-white hover:bg-red-90",
//         outline: "border bg-white text-black hover:bg-accent",
//         secondary: "bg-secondary text-white hover:bg-secondary-80",
//         ghost: "hover:bg-accent hover:text-accent-foreground",
//         link: "text-primary underline-offset-4 hover:underline",
//     },
//     size: {
//         default: "h-9 px-4 py-2",
//         sm: "h-8 rounded-md px-3",
//         lg: "h-10 rounded-md px-6",
//         icon: "h-9 w-9 rounded-md flex items-center justify-center",
//     },
// };

export class OwlButton extends Component {
    // static props = {
    //     variant: { type: String, optional: true },
    //     size: { type: String, optional: true },
    //     className: { type: String, optional: true },
    //     label: { type: String, optional: true },
    //     icon: { type: String, optional: true },
    //     disabled: { type: Boolean, optional: true },
    //     onClick: { type: Function, optional: true },
    // };

    //static template = "toolshub.owl_button_template"
    // get computedClass() {
    //     const v = this.props.variant || "default";
    //     const s = this.props.size || "default";
    //     return cn(
    //         "inline-flex items-center justify-center rounded-md font-medium transition-all disabled:opacity-50 outline-none",
    //         buttonVariants.variant[v],
    //         buttonVariants.size[s],
    //         this.props.className
    //     );
    // }

    // get getChild() {
    //     return Button;
    // }
}

OwlButton.template = "toolshub.owl_button_template"

registry.category("public_components").add("toolshub.owl_button", OwlButton);
