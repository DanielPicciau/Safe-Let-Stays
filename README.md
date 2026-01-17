# Safe Let Stays

A professional Django-based property rental and booking platform for Sheffield accommodation.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2+-green.svg)
![License](https://img.shields.io/badge/License-Proprietary-red.svg)

## 🏠 Overview

Safe Let Stays is a fully-featured property rental platform designed for corporates, contractors, and visitors seeking quality accommodation in Sheffield. The platform offers direct bookings, Stripe payment integration, and a modern React-enhanced frontend.

## ✨ Features

- **Property Listings**: Showcase properties with images, descriptions, and pricing
- **Smart Search**: Filter by location, capacity, beds, and dates
- **Secure Payments**: Stripe integration for seamless checkout
- **User Accounts**: Personal and business account support
- **Receipt Generation**: Automatic PDF receipts sent via email
- **Staff Panel**: Admin dashboard for property management
- **Security-First**: Comprehensive security middleware and protections
- **Responsive Design**: Modern UI with React components

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- pip (Python package manager)
- Git

### Local Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/DanielPicciau/Safe-Let-Stays.git
   cd Safe-Let-Stays
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or
   .venv\Scripts\activate     # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Visit** `http://localhost:8000`

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

| Variable | Description | Required |
|----------|-------------|----------|
| `DJANGO_SECRET_KEY` | Django secret key | ✅ |
| `DEBUG` | Debug mode (True/False) | ✅ |
| `ALLOWED_HOSTS` | Comma-separated hosts | ✅ |
| `STRIPE_PUBLISHABLE_KEY` | Stripe public key | ✅ |
| `STRIPE_SECRET_KEY` | Stripe secret key | ✅ |
| `STRIPE_WEBHOOK_SECRET` | Stripe webhook secret | ✅ |
| `MAILJET_API_KEY` | Mailjet API key | ✅ |
| `MAILJET_API_SECRET` | Mailjet API secret | ✅ |
| `GUESTY_API_KEY` | Guesty API key | ❌ |
| `GUESTY_API_SECRET` | Guesty API secret | ❌ |

## 📁 Project Structure

```
safeletstays/
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
├── .env.example             # Environment template
├── safeletstays/            # Django project settings
│   ├── settings.py          # Development settings
│   ├── settings_production.py  # Production settings
│   └── urls.py              # URL configuration
├── yourapp/                 # Main application
│   ├── models.py            # Database models
│   ├── views.py             # View controllers
│   ├── forms.py             # Form definitions
│   ├── admin.py             # Admin configuration
│   ├── security.py          # Security middleware
│   └── utils.py             # Utility functions
├── templates/               # HTML templates
├── static/                  # Static assets
└── media/                   # User uploads
```

## 🔒 Security

This project implements comprehensive security measures:

- **CSRF Protection**: Token validation on all forms
- **XSS Prevention**: Input sanitization and CSP headers
- **SQL Injection Protection**: Parameterized queries and validation
- **Rate Limiting**: Protection against brute force attacks
- **Session Security**: Secure cookie configuration
- **HTTPS Enforcement**: In production mode

See [SECURITY.md](SECURITY.md) for detailed security documentation.

## 🚀 Deployment

### PythonAnywhere

1. See [PYTHONANYWHERE_SETUP.md](PYTHONANYWHERE_SETUP.md) for detailed instructions
2. See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for step-by-step deployment

### Quick Deploy Commands

```bash
# Collect static files
python manage.py collectstatic --settings=safeletstays.settings_production

# Run migrations
python manage.py migrate --settings=safeletstays.settings_production
```

## 🧪 Testing

```bash
# Run all tests
python manage.py test

# Run security tests
python manage.py test yourapp.tests_security

# Run security audit
python security_audit.py
```

## 📧 Email Configuration

The project uses Mailjet for transactional emails. Configure your API credentials in `.env`:

```env
MAILJET_API_KEY=your_api_key
MAILJET_API_SECRET=your_api_secret
DEFAULT_FROM_EMAIL=Safe Let Stays <your-email@domain.com>
```

## 💳 Payment Integration

Stripe is used for payment processing. Test the integration:

1. Use Stripe test keys in development
2. Test card: `4242 4242 4242 4242`
3. Configure webhook endpoint: `/webhook/stripe/`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is proprietary software. All rights reserved.

## 📞 Support

For support, email daniel@webflare.studio or visit [safeletstays.co.uk](https://safeletstays.co.uk).

---

Built with ❤️ by [WebFlare Studio](https://webflare.studio)
