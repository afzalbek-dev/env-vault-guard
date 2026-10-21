import argparse
import sys
import os
from .parser import EnvParser
from .validator import EnvValidator
from .crypto import EnvCrypto


def main():
    parser = argparse.ArgumentParser(
        prog="env-vault-guard",
        description="CLI tool to validate .env completeness, detect drift, and securely encrypt secrets."
    )
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")

    # check command
    check_p = subparsers.add_parser("check", help="Compare .env against .env.example")
    check_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")
    check_p.add_argument("--example", default=".env.example", help="Path to .env.example (default: .env.example)")

    # encrypt command
    enc_p = subparsers.add_parser("encrypt", help="Encrypt .env file to .env.vault")
    enc_p.add_argument("--env", default=".env", help="Path to .env file (default: .env)")
    enc_p.add_argument("--out", default=".env.vault", help="Path to output vault file (default: .env.vault)")
    enc_p.add_argument("--passphrase", required=True, help="Passphrase to encrypt")

    # decrypt command
    dec_p = subparsers.add_parser("decrypt", help="Decrypt .env.vault to .env")
    dec_p.add_argument("--vault", default=".env.vault", help="Path to vault file (default: .env.vault)")
    dec_p.add_argument("--out", default=".env.decrypted", help="Path to output file")
    dec_p.add_argument("--passphrase", required=True, help="Passphrase to decrypt")

    # generate-example command
    gen_p = subparsers.add_parser("generate-example", help="Generate a sanitized .env.example from an existing .env")
    gen_p.add_argument("--env", default=".env", help="Path to .env file")
    gen_p.add_argument("--out", default=".env.example", help="Output path for .env.example")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "check":
        validator = EnvValidator()
        try:
            res = validator.validate_files(args.env, args.example)
            print(res.summary())
            if not res.is_valid:
                sys.exit(1)
        except Exception as e:
            print(f"Error during validation: {e}")
            sys.exit(1)

    elif args.command == "encrypt":
        try:
            with open(args.env, "r", encoding="utf-8") as f:
                content = f.read()
            encrypted = EnvCrypto.encrypt(content, args.passphrase)
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(encrypted)
            print(f"✅ Successfully encrypted '{args.env}' to '{args.out}'")
        except Exception as e:
            print(f"Encryption error: {e}")
            sys.exit(1)

    elif args.command == "decrypt":
        try:
            with open(args.vault, "r", encoding="utf-8") as f:
                payload = f.read().strip()
            decrypted = EnvCrypto.decrypt(payload, args.passphrase)
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(decrypted)
            print(f"✅ Successfully decrypted '{args.vault}' to '{args.out}'")
        except Exception as e:
            print(f"Decryption error: {e}")
            sys.exit(1)

    elif args.command == "generate-example":
        try:
            env_data = EnvParser.parse_file(args.env)
            sanitized = {k: "your_" + k.lower() for k in env_data.keys()}
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(EnvParser.dump(sanitized))
            print(f"✅ Generated template '{args.out}' with {len(sanitized)} keys.")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)


if __name__ == "__main__":
    main()
