import hashlib
import json
import unittest

import monkey.code_configuration as configuration
from monkey.sources.compiled import ParseError


def row(row_id, dish_id, ingredients, *, cookware=-1, duration=12, cook_type=1):
    return dict(id=row_id, elementOrderId=cookware,
                needElements={str(key): value for key, value in ingredients},
                elementIdWeight={str(dish_id): 0}, duration=duration,
                cookType=cook_type, addElementStorage=1, speedUpCost=1)


class ElementMultiOrderPoolTests(unittest.TestCase):
    def setUp(self):
        self.original_table_sha = configuration.TABLE_SHA256
        self.original_source_sha = configuration.SOURCE_SHA256
        self.original_spans = configuration.SOURCE_SPANS
        source = bytearray(b'fixture-source:')
        spans = {}
        for name in configuration.SOURCE_SPANS:
            fragment = ('static-fixture-span:' + name).encode()
            start = len(source)
            source.extend(fragment)
            spans[name] = dict(byteOffset=start, byteLength=len(fragment),
                               sha256=hashlib.sha256(fragment).hexdigest())
        self.source = bytes(source)
        configuration.SOURCE_SPANS = spans
        self.document = {
            # The keys are deliberately non-numeric insertion order. The source
            # `for...in` decoder visits canonical integer keys in numeric order.
            '10': row(10, 900, [(4, 1), (901, 2), (7, 1)], cook_type=0),
            '2': row(2, 901, [(4, 3), (5, 1)]),
        }
        self.table = json.dumps(self.document, separators=(',', ':')).encode()
        configuration.TABLE_SHA256 = hashlib.sha256(self.table).hexdigest()
        configuration.SOURCE_SHA256 = hashlib.sha256(self.source).hexdigest()

    def tearDown(self):
        configuration.TABLE_SHA256 = self.original_table_sha
        configuration.SOURCE_SHA256 = self.original_source_sha
        configuration.SOURCE_SPANS = self.original_spans

    def map(self, document=None):
        table = self.table if document is None else json.dumps(document, separators=(',', ':')).encode()
        if document is not None:
            configuration.TABLE_SHA256 = hashlib.sha256(table).hexdigest()
        return configuration.map_payload(table, self.source,
                    expected_table_sha256=configuration.TABLE_SHA256,
                    expected_source_sha256=configuration.SOURCE_SHA256, root_dish_id=900)

    def test_maps_exact_recipe_fields_and_recursive_first_seen_leaf_order(self):
        result = self.map()
        self.assertEqual(result['status'], 'validated-finite-source-subset')
        self.assertEqual(result['table']['rowCount'], 2)
        self.assertEqual([r['sourceRowId'] for r in result['recipes']], [2, 10])
        root = next(r for r in result['recipes'] if r['sourceRowId'] == 10)
        self.assertEqual(root['recipe'], dict(id=10, dish=900, ingredients=[[4, 1], [7, 1], [901, 2]]))
        # Kp's source expression explicitly normalizes non-positive cookType to 1.
        self.assertEqual(root['cookType'], 1)
        self.assertEqual(result['representative'], dict(
            rootDishId=900, rootSourceRowId=10, expandedRecipeDishIds=[900, 901],
            leafOccurrences=[4, 7, 4, 5], flattenedLeaves=[4, 7, 5]))
        self.assertFalse(result['source']['sourceExecuted'])

    def test_duplicate_dish_and_numeric_key_collisions_are_rejected(self):
        duplicate_dish = {'1': row(1, 900, [(4, 1)]), '2': row(2, 900, [(5, 1)])}
        with self.assertRaises(ParseError) as caught:
            self.map(duplicate_dish)
        self.assertEqual(caught.exception.code, 'CODE_CONFIG_DUPLICATE_DISH')
        collided_keys = row(1, 900, [(4, 1), (4, 2)])
        collided_keys['needElements'] = {'4': 1, '04': 2}
        with self.assertRaises(ParseError) as caught:
            self.map({'1': collided_keys})
        self.assertEqual(caught.exception.code, 'CODE_CONFIG_DUPLICATE_INGREDIENT')
        duplicate_prefix = {'1': row(1, 900, [(4, 1)])}
        duplicate_prefix['1']['elementIdWeight'] = {'900': 1, '900_2': 2}
        with self.assertRaises(ParseError) as caught:
            self.map(duplicate_prefix)
        self.assertEqual(caught.exception.code, 'CODE_CONFIG_DUPLICATE_DISH')

    def test_cycles_and_unsupported_shapes_are_rejected(self):
        cycle = {'1': row(1, 900, [(901, 1)]), '2': row(2, 901, [(900, 1)])}
        with self.assertRaises(ParseError) as caught:
            self.map(cycle)
        self.assertEqual(caught.exception.code, 'CODE_CONFIG_RECIPE_CYCLE')
        unsupported = {'1': row(1, 900, [(4, True)])}
        with self.assertRaises(ParseError) as caught:
            self.map(unsupported)
        self.assertEqual(caught.exception.code, 'CODE_CONFIG_VALUE')

    def test_wrong_source_identity_and_unrecognized_code_shape_are_rejected(self):
        with self.assertRaises(ParseError) as caught:
            configuration.map_payload(self.table, self.source, expected_table_sha256='0' * 64,
                expected_source_sha256=configuration.SOURCE_SHA256, root_dish_id=900)
        self.assertEqual(caught.exception.code, 'CODE_CONFIG_TABLE_IDENTITY')
        span = configuration.SOURCE_SPANS['flattenIngredientsOf']
        bad_source = bytearray(self.source)
        bad_source[span['byteOffset']] ^= 1
        bad_source = bytes(bad_source)
        configuration.SOURCE_SHA256 = hashlib.sha256(bad_source).hexdigest()
        with self.assertRaises(ParseError) as caught:
            configuration.map_payload(self.table, bad_source,
                expected_table_sha256=configuration.TABLE_SHA256,
                expected_source_sha256=hashlib.sha256(bad_source).hexdigest(), root_dish_id=900)
        self.assertEqual(caught.exception.code, 'CODE_CONFIG_SOURCE_CONTRACT')


if __name__ == '__main__':
    unittest.main()
