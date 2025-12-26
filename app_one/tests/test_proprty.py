from  odoo.tests.common import TransactionCase
class TestProperty(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestProperty, self).setUp()
        self.property_01_record = self.env['property'].create({
            'name': 'property 10',
            'postcode':'12345',
            'bedrooms': 3,

        })
        def test_01_property_values(self):
            propert_id = self.property_01_record
            self.assertRecordValues(propert_id, [{
                'name': 'property 10',
                'postcode': '12345',
                'bedrooms': 3,
            }])