openerp.pos_thai = function (instance) {
    var module = instance.point_of_sale;
    var _t = instance.web._t;

    var round_pr = instance.web.round_precision

    var PosModelSuper = module.PosModel
    module.PosModel = module.PosModel.extend({

        load_server_data: function () {
            var self = this;
            var loaded = PosModelSuper.prototype.load_server_data.call(this);

            loaded = loaded.then(function () {
                return self.fetch(
                    'res.partner',
                    ['sys_pos_disc'],
                    [['customer','=',true]],
                    {}
                );

            }).then(function (partners) {
                $.each(partners, function () {
                    $.extend(self.db.get_partner_by_id(this.id) || {}, this)
                });
                return $.when()
            })
            return loaded;
        },


    })


    module.Order = module.Order.extend({


        addProduct: function (product, options) {
            //#############################################3
            console.log(product);

            var order = this.pos.get('selectedOrder');
            var client = order.get_client();

            if (client != null) {
                var discount = client.sys_pos_disc;
                if (discount>0) {
                    $.each(order.get('orderLines').models, function (k, line) {
                        line.set_discount(discount)
                    })
                }

            }
            //#############################################3


            if (this._printed) {
                this.destroy();
                return this.pos.get('selectedOrder').addProduct(product, options);
            }
            options = options || {};
            var attr = JSON.parse(JSON.stringify(product));
            attr.pos = this.pos;
            attr.order = this;
            var line = new module.Orderline({}, {pos: this.pos, order: this, product: product});

            if (options.quantity !== undefined) {
                line.set_quantity(options.quantity);
            }
            if (options.price !== undefined) {
                line.set_unit_price(options.price);
            }
            if (discount > 0) {
                line.set_discount(discount);
            }

            var last_orderline = this.getLastOrderline();
            if (last_orderline && last_orderline.can_be_merged_with(line) && options.merge !== false) {
                last_orderline.merge(line);
            } else {
                this.get('orderLines').add(line);
            }
            this.selectLine(this.getLastOrderline());
        },

    })


}