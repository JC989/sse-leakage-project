from unittest import TestCase

from sseleak.search import SearchClient, lookup


class SearchClientTest(TestCase):
    def test_lookup_decrypts_to_unique_matching_record_ids(self) -> None:
        records = [
            ["diabetes", "diabetes", "appointment"],
            ["appointment", "blood"],
            ["diabetes", "medication"],
        ]
        client = SearchClient()
        index = client.build_index(records)

        for keyword, expected_ids in [
            ("diabetes", [0, 2]),
            ("appointment", [0, 1]),
            ("blood", [1]),
            ("medication", [2]),
            ("asthma", []),
        ]:
            with self.subTest(keyword=keyword):
                encrypted_ids = lookup(index, client.make_token(keyword))
                self.assertEqual(client.decrypt_ids(encrypted_ids), expected_ids)
