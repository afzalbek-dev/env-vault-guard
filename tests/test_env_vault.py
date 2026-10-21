import unittest
from env_vault_guard import EnvParser, EnvValidator, EnvCrypto


class TestEnvVaultGuard(unittest.TestCase):
    def test_env_parser(self):
        text = """
        # Comment line
        export DATABASE_URL=postgres://localhost/db
        API_KEY="my-secret-key"
        DEBUG=false # inline comment
        """
        data = EnvParser.parse_text(text)
        self.assertEqual(data["DATABASE_URL"], "postgres://localhost/db")
        self.assertEqual(data["API_KEY"], "my-secret-key")
        self.assertEqual(data["DEBUG"], "false")

    def test_env_validator_drift(self):
        example = {"PORT": "8000", "DB_NAME": "app", "SECRET_KEY": "xxx"}
        env = {"PORT": "8000", "SECRET_KEY": "123456", "EXTRA_KEY": "val"}

        validator = EnvValidator()
        res = validator.compare(env, example)

        self.assertFalse(res.is_valid)
        self.assertIn("DB_NAME", res.missing_keys)
        self.assertIn("EXTRA_KEY", res.undocumented_keys)
        self.assertIn("SECRET_KEY", res.weak_secrets)

    def test_crypto_encryption_and_decryption(self):
        plaintext = "DATABASE_URL=postgres://user:pass@host:5432/db\nAPI_KEY=live_sec_12345"
        passphrase = "super-secure-passphrase-2026"

        encrypted = EnvCrypto.encrypt(plaintext, passphrase)
        self.assertNotEqual(encrypted, plaintext)

        decrypted = EnvCrypto.decrypt(encrypted, passphrase)
        self.assertEqual(decrypted, plaintext)

    def test_crypto_tampering_fails(self):
        plaintext = "SECRET=val"
        passphrase = "password123"
        encrypted = EnvCrypto.encrypt(plaintext, passphrase)

        # Wrong passphrase
        with self.assertRaises(ValueError):
            EnvCrypto.decrypt(encrypted, "wrong-passphrase")


if __name__ == "__main__":
    unittest.main()
