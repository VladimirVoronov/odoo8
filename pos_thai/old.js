/**
 * Created by vovan on 17.09.15.
 */



    instance.point_of_sale.ScreenWidget.include({
        show: function () {
            this._super()
            console.log('myPaymentScreenWidget show');
            var self = this;

            var print_gift_ticket_button = this.add_action_button({
                label: _t('Gift Ticketsss'),
                icon: '/point_of_sale/static/src/img/icons/png48/printer.png',
                click: function () {
                    console.log('my PaymentScreenWidget showxxxxxxxxx1111');
                },
            });

            this.add_action_button({
                label: _t('Cashsss2'),
                name: 'cashboxsss2',
                icon: '/point_of_sale/static/src/img/open-cashbox.png',
                click: function () {
                    console.log('my PaymentScreenWidget showxxxxxx');
                },
            });
        },


    });

    instance.point_of_sale.PaymentScreenWidget.include({
        show: function () {
            this._super()
            console.log('myPaymentScreenWidget show');
            var self = this;

            var print_gift_ticket_button = this.add_action_button({
                label: _t('Gift Ticketzzzz'),
                icon: '/point_of_sale/static/src/img/icons/png48/printer.png',
                click: function () {
                    console.log('my PaymentScreenWidget showxxxxxxxxx1111');
                },
            });

            this.add_action_button({
                label: _t('Cashzzz'),
                name: 'cashboxzzz',
                icon: '/point_of_sale/static/src/img/open-cashbox.png',
                click: function () {
                    console.log('my PaymentScreenWidget showxxxxxx');
                },
            });
        },


    });