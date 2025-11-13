'use client';

import { useProducts } from '@/features/products/hooks/useProduct'; // Import hook to fetch products
import Link from 'next/link';

export default function ProductsPage() {
  // Fetching products with optional filters (e.g., search term, category)
  const { data: products, isLoading, error } = useProducts();

  // Handling loading state
  if (isLoading) {
    return <div className="text-center text-xl">Loading products...</div>;
  }

  // Handling error state
  if (error) {
    return <div className="text-center text-xl text-red-500">Error fetching products</div>;
  }

  // Ensure products is an array before mapping
  const productList = Array.isArray(products) ? products : [];  // Safely access products array

  return (
    <div className="products-list container mx-auto px-4 py-6">
      <h1 className="text-3xl font-semibold text-center mb-6">Products</h1>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {productList.length > 0 ? (
          productList.map((product) => (
            <div key={product.id} className="product-card bg-white p-4 rounded-lg shadow-lg">
              <img
                src={product.image}
                alt={product.name}
                className="product-image w-full h-48 object-cover rounded-t-lg mb-4"
              />
              <h3 className="text-xl font-medium">{product.name}</h3>
              <p className="text-gray-500 text-sm">{product.description.slice(0, 100)}...</p>
              <Link
                href={`/products/${product.slug}`}
                className="btn btn-primary mt-4 inline-block bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition"
              >
                View Details
              </Link>
            </div>
          ))
        ) : (
          <div className="text-center text-xl text-gray-600">No products available.</div>
        )}
      </div>
    </div>
  );
}
