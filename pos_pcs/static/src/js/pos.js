openerp.pos_pcs = function (instance) {
    var module = instance.point_of_sale;
    var _t = instance.web._t;

    var round_pr = instance.web.round_precision


    instance.point_of_sale.PaypadWidget.include({

        renderElement: function () {
            var self = this;
            this._super()
            this.$el.empty();

            $(this.el).append('<ul class="pos-actionbar-button-list"><li id="next_button" class="button "><div class="icon"><img src="/point_of_sale/static/src/img/icons/png48/go-next.png"><div class="iconlabel">Next Order</div></div></li></ul>');

            $(this.el).on('click', '#next_button', function () {

                var order = self.pos.get('selectedOrder');

                if (order.get('orderLines').models.length === 0) {
                    self.pos_widget.screen_selector.show_popup('error', {
                        'message': _t('Empty Order'),
                        'comment': _t('There must be at least one product in your order before it can be validated'),
                    });
                    return;
                }

                if (order.get('client') === null) {
                    self.pos_widget.screen_selector.show_popup('error', {
                        'message': _t('Empty Client'),
                        'comment': _t('Order must have Client'),
                    });
                    return;
                }

                $.when(order.getClientSalesBalance()).then(function (result) {

                    var total = order ? order.getTotalTaxIncluded() : 0;
                    var taxes = order ? total - order.getTotalTaxExcluded() : 0;
                    var client_balance = result.balance - total;

                    if (client_balance < 0) {

                        self.pos.pos_widget.screen_selector.show_popup('error', {
                            'message': _t('Client Balance error'),
                            'comment': _t('Insufficient funds in the Client account. Current client balance =' + (result.balance - total)),
                        });

                        return;
                    }

                    if (client_balance >= 0) {

                        self.pos.push_order(order);
                         order.destroy();
                    }

                });

            });


        }

    });

    module.OrderWidget.include({

        update_summary: function () {

            var order = this.pos.get('selectedOrder');
            var self = this;

            $.when(order.getClientSalesBalance()).then(function (result) {

                var total = order ? order.getTotalTaxIncluded() : 0;
                var taxes = order ? total - order.getTotalTaxExcluded() : 0;
                var client_balance = result.balance - total;

                self.el.querySelector('.summary .total > .value').textContent = self.format_currency(total);
                self.el.querySelector('.summary .total .subentry .value').textContent = self.format_currency(taxes);
                self.el.querySelector('#client_balance').textContent = self.format_currency(client_balance);

            });


        },
    })

    var OrderSuper = module.Order;
    module.Order = module.Order.extend({

        getClientSalesBalance: function () {

            var order = this.pos.get('selectedOrder');

            client = order.get_client();
            var bal = new $.Deferred();
            bal.balance = 0;

            if (client == null) {
                return 0.00;
            }

            new instance.web.Model('res.partner').call('get_partner_balance', [client]).then(function (balance) {
                    bal.balance = balance;
                    bal.resolve(bal);

                },
                function (err, event) {
                });

            return bal;
        },

        addProduct: function () {
            var _this = this;
            var order = _this.pos.get('selectedOrder');
            var args = arguments;

            client = order.get_client();

            if (client == null) {
                _this.pos.pos_widget.screen_selector.show_popup('error', {
                    'message': _t('Client error'),
                    'comment': _t('Please set Client before start sale'),
                });

                return;
            }

            $.when(order.getClientSalesBalance()).then(function (result) {

                var total = order ? order.getTotalTaxIncluded() : 0;
                var taxes = order ? total - order.getTotalTaxExcluded() : 0;
                var client_balance = result.balance - total - args[0].price;

                if (client_balance < 0) {
                    _this.pos.pos_widget.order_widget.update_summary();

                    _this.pos.pos_widget.screen_selector.show_popup('error', {
                        'message': _t('Client Balance error'),
                        'comment': _t('Insufficient funds in the Client account. Current client balance =' + (result.balance - total)),
                    });

                    return;
                }

                OrderSuper.prototype.addProduct.apply(_this, args);

            });


        },

    })


}