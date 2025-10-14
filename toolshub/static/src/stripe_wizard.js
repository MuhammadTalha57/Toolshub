odoo.define('toolshub.stripe_wizard', function(require){
    "use strict";

    var FormController = require('web.FormController');

    FormController.include({
        renderElement: function () {
            this._super.apply(this, arguments);

            var self = this;
            var stripeDiv = this.$('.o_stripe_elements');
            if (stripeDiv.length) {
                var stripe = Stripe('pk_test_XXXXXXXXXXXXXXXX'); // publishable key
                var elements = stripe.elements();
                var card = elements.create('card');
                card.mount(stripeDiv[0]);

                this.$('button.btn-primary').on('click', async function(ev){
                    ev.preventDefault();
                    var result = await stripe.createPaymentMethod({
                        type: 'card',
                        card: card,
                    });
                    if(result.error){
                        alert(result.error.message);
                    } else {
                        // fill hidden field in wizard
                        self.$('input[name="payment_method_id"]').val(result.paymentMethod.id);
                        self.saveRecord();
                    }
                });
            }
        }
    });
});
