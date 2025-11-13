import './globals.css';
import { AuthProvider } from '../contexts/AuthContext';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';
import QueryProvider from '@/utils/QueryProvider'; // <-- import the new provider

export const metadata = {
  title: 'MedInn',
  description: 'Ecommerce frontend',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="flex flex-col min-h-screen">
        <QueryProvider>
          <AuthProvider>
            <Navbar />
            <main className="flex-grow">{children}</main>
            <Footer />
          </AuthProvider>
        </QueryProvider>
      </body>
    </html>
  );
}
