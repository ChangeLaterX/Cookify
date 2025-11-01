# Cookify

A comprehensive pantry management and recipe suggestion app built with React Native, Expo, and FastAPI.

## Features

- 📱 Cross-platform mobile app (iOS, Android, Web)
- 🔐 Secure authentication with Supabase
- 📦 Pantry inventory management
- ⏰ Expiration tracking and alerts
- 🍳 Recipe suggestions based on available ingredients
- 🛒 Smart shopping list generation
- 📸 Receipt scanning capability (placeholder)

## Tech Stack

- **Frontend**: React Native, Expo, TypeScript
- **Backend**: Python FastAPI
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **State Management**: React Context

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.9+
- Expo CLI
- Supabase account

### Installation

1. Clone the repository:
```bash
git clone https://github.com/ChangeLaterX/Cookify.git
cd Cookify
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Add your Supabase credentials

4. Start the development server:
```bash
npm run dev
```

### Development

- Mobile app: `npm run dev:mobile`
- Backend: `cd backend && uvicorn main:app --reload`
- Build web: `npm run build:web`

## Project Structure

```
├── mobile/          # React Native app with Expo
├── backend/         # Python FastAPI server
└── shared/          # Shared TypeScript types and utilities
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.