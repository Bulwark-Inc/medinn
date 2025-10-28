export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-4 mt-12">
      <div className="max-w-7xl mx-auto text-center">
        <p>&copy; {new Date().getFullYear()} MedInn. All rights reserved.</p>
      </div>
    </footer>
  );
}
