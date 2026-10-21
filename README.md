# 🔒 Env Vault Guard

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Zero Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen.svg)]()

Loyihangizdagi `.env` va `.env.example` o'rtasidagi farqlarni (drift) aniqlash, yetishmayotgan konfiguratsiyalarni tekshirish, zaif/namuna parollarni aniqlash hamda maxfiy konfiguratsiyalarni xavfsiz shifrlab saqlash uchun mo'ljallangan CLI vositasi va Python kutubxonasi.

---

## 🌟 Imkoniyatlari

- **Avtomatlashtirilgan Drift Detection:** `.env.example` da bor, lekin `.env` da unutilgan o'zgaruvchilarni tezkor aniqlaydi.
- **CI/CD Integratsiyasi:** Konfiguratsiyada xatolik bo'lsa `exit code 1` qaytaradi, bu esa noaniq env bilan deploy bo'lib ketishini to'xtatadi.
- **Zaif Parollar Skaneri:** `123456`, `secret`, `changeme` kabi test qiymatlar qolib ketganligini ogohlantiradi.
- **Xavfsiz Vault Shifrlash:** PBKDF2 va HMAC autentifikatsiyalangan shifrlash orqali `.env` faylini `.env.vault` ko'rinishida xavfsiz arxivlaydi.
- **Nol tashqi bog'liqlik:** Sof Python standart kutubxonasida ishlaydi.

---

## 🚀 O'rnatish

```bash
git clone https://github.com/afzalbek-dev/env-vault-guard.git
cd env-vault-guard
pip install .
```

---

## 💻 CLI Buyruqlari

### 1. `.env` To'liqligini Tekshirish (CI/CD uchun)
```bash
env-vault-guard check --env .env --example .env.example
```

Chiqish namunasi:
```text
❌ Environment variables check FAILED.
  - Missing keys (in example but not in env): REDIS_HOST, STRIPE_SECRET_KEY
  - Warning: Weak/default dummy secrets detected: JWT_SECRET
```

### 2. Mavjud `.env` dan Avtomatik `.env.example` Yaratish
```bash
env-vault-guard generate-example --env .env --out .env.example
```

### 3. Maxfiy `.env` Faylini Shifrlash
```bash
env-vault-guard encrypt --env .env --out .env.vault --passphrase "maxfiy_parol"
```

### 4. Shifrlangan Faylni Tiklash
```bash
env-vault-guard decrypt --vault .env.vault --out .env --passphrase "maxfiy_parol"
```

---

## 🐍 Python SDK Sifatida Foydalanish

```python
from env_vault_guard import EnvValidator, EnvCrypto

validator = EnvValidator()
result = validator.validate_files(".env", ".env.example")

if not result.is_valid:
    print("Yetishmayotgan kalitlar:", result.missing_keys)
```

---

## 🧪 Testlash

```bash
python3 -m unittest discover tests -v
```

---

## 📄 Litsenziya

MIT License. Muallif: [Afzalbek](https://github.com/afzalbek-dev).
