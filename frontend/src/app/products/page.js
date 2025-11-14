'use client';

import { useState, useEffect } from 'react';
import { useProducts } from '@/features/products/hooks/useProduct';
import Link from 'next/link';

const ProductsPage = () => {
  // State for the search field and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minRating, setMinRating] = useState('');
  const [inStock, setInStock] = useState(false);

  // State to trigger applying filters
  const [filters, setFilters] = useState({});

  // Fetch categories (for filter selection)
  const [categories, setCategories] = useState([]);
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/products/categories/');
        const data = await response.json();
        setCategories(data);
      } catch (error) {
        console.error('Error fetching categories:', error);
      }
    };
    fetchCategories();
  }, []);

  // Fetch products based on filters
  const { data: products, isLoading, error } = useProducts(filters);

  // Handle changes in the filter section
  const handleFilterChange = () => {
    setFilters({
      category: categoryFilter,
      min_price: minPrice,
      max_price: maxPrice,
      min_rating: minRating,
      in_stock: inStock ? true : undefined, // only send in_stock if true
      search: searchTerm,
    });
  };

  const handleSearchChange = (e) => setSearchTerm(e.target.value);
  const handleCategoryChange = (e) => setCategoryFilter(e.target.value);
  const handleMinPriceChange = (e) => setMinPrice(e.target.value);
  const handleMaxPriceChange = (e) => setMaxPrice(e.target.value);
  const handleMinRatingChange = (e) => setMinRating(e.target.value);
  const handleInStockChange = () => setInStock(!inStock);

  const handleApplyFilters = () => {
    handleFilterChange(); // Apply the current filters
  };

  // Handle loading and error states
  if (isLoading) return <div className="text-center text-xl">Loading products...</div>;
  if (error) return <div className="text-center text-xl text-red-500">Error fetching products</div>;

  // Ensure products is an array before mapping
  const productList = Array.isArray(products.results) ? products.results : [];

  return (
    <div className="container mx-auto px-4 py-6">
      <h1 className="text-3xl font-semibold text-center mb-6">Products</h1>

      {/* Search Input */}
      <div className="mb-6 flex items-center space-x-2">
        <input
          type="text"
          value={searchTerm}
          onChange={handleSearchChange}
          placeholder="Search products..."
          className="p-2 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button
          onClick={handleApplyFilters}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Search
        </button>
      </div>

      {/* Filter Section */}
      <div className="mb-8">
        <h3 className="text-xl font-semibold text-gray-700 mb-4">Filter Products</h3>

        {/* Category Filter */}
        <div className="mb-4">
          <label htmlFor="category" className="block text-sm font-medium text-gray-600 mb-2">Category</label>
          <select
            id="category"
            value={categoryFilter}
            onChange={handleCategoryChange}
            className="p-2 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Select Category</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>
        </div>

        {/* Price Range Filters */}
        <div className="mb-4 grid grid-cols-2 gap-4">
          <div>
            <label htmlFor="minPrice" className="block text-sm font-medium text-gray-600 mb-2">Min Price</label>
            <input
              type="number"
              id="minPrice"
              value={minPrice}
              onChange={handleMinPriceChange}
              placeholder="Min Price"
              className="p-2 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label htmlFor="maxPrice" className="block text-sm font-medium text-gray-600 mb-2">Max Price</label>
            <input
              type="number"
              id="maxPrice"
              value={maxPrice}
              onChange={handleMaxPriceChange}
              placeholder="Max Price"
              className="p-2 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* Rating Filter */}
        <div className="mb-4">
          <label htmlFor="minRating" className="block text-sm font-medium text-gray-600 mb-2">Min Rating</label>
          <input
            type="number"
            id="minRating"
            value={minRating}
            onChange={handleMinRatingChange}
            placeholder="Min Rating"
            max="5"
            min="1"
            className="p-2 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* In Stock Filter */}
        <div className="mb-6 flex items-center space-x-2">
          <label htmlFor="inStock" className="text-sm font-medium text-gray-600">In Stock</label>
          <input
            type="checkbox"
            id="inStock"
            checked={inStock}
            onChange={handleInStockChange}
            className="h-4 w-4 text-blue-600 border-gray-300 rounded"
          />
        </div>

        {/* Apply Filters Button */}
        <button
          onClick={handleApplyFilters}
          className="px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          Apply Filters
        </button>
      </div>

      {/* Product List Display */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
        {productList.length > 0 ? (
          productList.map((product) => (
            <div key={product.id} className="product-card bg-white p-4 rounded-lg shadow-lg hover:shadow-xl transition-shadow">
              <img
                src={product.image}
                alt={product.name}
                className="w-full h-48 object-cover rounded-t-lg mb-4"
              />
              <h3 className="text-xl font-medium text-gray-800">{product.name}</h3>
              <p className="text-gray-500 text-sm">{product.description.slice(0, 100)}...</p>
              <p className="font-semibold text-gray-800 mt-2">${product.price}</p>
              <p className="text-sm text-gray-600 mt-1">Stock: {product.stock}</p>
              <p className="text-sm text-gray-600">Rating: {product.average_rating} ({product.review_count} reviews)</p>
              <Link
                href={`/products/${product.slug}`}
                className="mt-4 inline-block bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 transition"
              >
                View Details
              </Link>
            </div>
          ))
        ) : (
          <div className="text-center text-xl text-gray-600">No products available.</div>
        )}
      </div>

      {/* Pagination (if available) */}
      {products?.next && (
        <button
          onClick={() => setFilters({ ...filters, page: products.next })}
          className="mt-6 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          Load More
        </button>
      )}
    </div>
  );
};

export default ProductsPage;
