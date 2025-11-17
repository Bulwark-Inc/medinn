'use client';

import { useState, useEffect } from 'react';
import { useProducts, useCategories } from '@/features/products/hooks/useProduct';
import Link from 'next/link';
import AddToCartButton from '@/features/cart/components/AddToCartButton';

const ProductsPage = () => {
  // State for the search field and filters
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [minPrice, setMinPrice] = useState('');
  const [maxPrice, setMaxPrice] = useState('');
  const [minRating, setMinRating] = useState('');
  const [inStock, setInStock] = useState(false);
  const [sortBy, setSortBy] = useState('');

  // State to trigger applying filters
  const [filters, setFilters] = useState({});

  // Collapsible state
  const [isFiltersOpen, setIsFiltersOpen] = useState(true);

  // Fetch categories
  const { data: categories, isLoading: loadingCategories } = useCategories();

  // Fetch products based on filters
  const { data: products, isLoading, error } = useProducts(filters);

  // Handle search submission
  const handleSearch = (e) => {
    e.preventDefault();
    const newFilters = {
      ...filters,
      search: searchTerm || undefined,
    };
    
    // Remove undefined values
    Object.keys(newFilters).forEach(key => 
      newFilters[key] === undefined && delete newFilters[key]
    );

    setFilters(newFilters);
  };

  // Handle applying filters
  const handleApplyFilters = () => {
    const newFilters = {
      search: searchTerm || undefined,
      category: categoryFilter || undefined,
      min_price: minPrice || undefined,
      max_price: maxPrice || undefined,
      min_rating: minRating || undefined,
      in_stock: inStock || undefined,
      ordering: sortBy || undefined,
    };

    // Remove undefined values
    Object.keys(newFilters).forEach(key => 
      newFilters[key] === undefined && delete newFilters[key]
    );

    setFilters(newFilters);
  };

  // Clear all filters
  const handleClearFilters = () => {
    setSearchTerm('');
    setCategoryFilter('');
    setMinPrice('');
    setMaxPrice('');
    setMinRating('');
    setInStock(false);
    setSortBy('');
    setFilters({});
  };

  // Handle loading state
  if (isLoading && !products) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading products...</p>
          </div>
        </div>
      </div>
    );
  }

  // Handle error state
  if (error) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <div className="text-red-500 text-xl mb-4">Error loading products</div>
          <button
            onClick={() => window.location.reload()}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  // Ensure products is an array before mapping
  const productList = Array.isArray(products?.results) ? products.results : [];
  const hasActiveFilters = Object.keys(filters).length > 0;

  // Count active filters (excluding search)
  const activeFilterCount = Object.keys(filters).filter(key => key !== 'search').length;

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-3xl font-semibold">Products</h1>
        <div className="text-sm text-gray-600">
          {products?.count ? `${products.count} products found` : ''}
        </div>
      </div>

      {/* Search Bar - Separated and Prominent */}
      <div className="mb-6">
        <form onSubmit={handleSearch} className="max-w-3xl">
          <div className="flex gap-2">
            <div className="flex-1 relative">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search for products..."
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <svg
                className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <button
              type="submit"
              className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
            >
              Search
            </button>
          </div>
        </form>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Left Sidebar - Filters */}
        <aside className="lg:col-span-1 space-y-6">
          {/* Collapsible Filters Box */}
          <div className="bg-white rounded-lg shadow-md overflow-hidden sticky top-4">
            {/* Filter Header */}
            <button
              onClick={() => setIsFiltersOpen(!isFiltersOpen)}
              className="w-full p-4 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-gray-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                </svg>
                <h3 className="text-lg font-semibold text-gray-700">Filters</h3>
                {activeFilterCount > 0 && (
                  <span className="bg-blue-600 text-white text-xs font-bold px-2 py-1 rounded-full">
                    {activeFilterCount}
                  </span>
                )}
              </div>
              <svg
                className={`w-5 h-5 text-gray-600 transition-transform ${isFiltersOpen ? 'transform rotate-180' : ''}`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Filter Content */}
            {isFiltersOpen && (
              <div className="p-6">
                {hasActiveFilters && (
                  <button
                    onClick={handleClearFilters}
                    className="text-sm text-red-600 hover:text-red-800 transition-colors mb-4 flex items-center gap-1"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                    Clear All Filters
                  </button>
                )}

                {/* Category Filter */}
                <div className="mb-4">
                  <label htmlFor="category" className="block text-sm font-medium text-gray-700 mb-2">
                    Category
                  </label>
                  <select
                    id="category"
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    disabled={loadingCategories}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
                  >
                    <option value="">All Categories</option>
                    {Array.isArray(categories) && categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Price Range Filters */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Price Range
                  </label>
                  <div className="grid grid-cols-2 gap-2">
                    <input
                      type="number"
                      value={minPrice}
                      onChange={(e) => setMinPrice(e.target.value)}
                      placeholder="Min"
                      min="0"
                      className="p-2 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                    <input
                      type="number"
                      value={maxPrice}
                      onChange={(e) => setMaxPrice(e.target.value)}
                      placeholder="Max"
                      min="0"
                      className="p-2 border border-gray-300 rounded-lg w-full focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                {/* Rating Filter */}
                <div className="mb-4">
                  <label htmlFor="minRating" className="block text-sm font-medium text-gray-700 mb-2">
                    Minimum Rating
                  </label>
                  <select
                    id="minRating"
                    value={minRating}
                    onChange={(e) => setMinRating(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Any Rating</option>
                    <option value="4">4★ & above</option>
                    <option value="3">3★ & above</option>
                    <option value="2">2★ & above</option>
                    <option value="1">1★ & above</option>
                  </select>
                </div>

                {/* Sort By */}
                <div className="mb-4">
                  <label htmlFor="sortBy" className="block text-sm font-medium text-gray-700 mb-2">
                    Sort By
                  </label>
                  <select
                    id="sortBy"
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Default</option>
                    <option value="price">Price: Low to High</option>
                    <option value="-price">Price: High to Low</option>
                    <option value="-average_rating">Highest Rated</option>
                    <option value="-created_at">Newest First</option>
                  </select>
                </div>

                {/* In Stock Filter */}
                <div className="mb-6">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={inStock}
                      onChange={(e) => setInStock(e.target.checked)}
                      className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm font-medium text-gray-700">In Stock Only</span>
                  </label>
                </div>

                {/* Apply Filters Button */}
                <button
                  onClick={handleApplyFilters}
                  className="w-full px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                >
                  Apply Filters
                </button>
              </div>
            )}
          </div>

          {/* Trending/Featured Box */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-orange-500" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              Trending Now
            </h3>
            <div className="space-y-3">
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">Wireless Headphones</div>
                <div className="text-xs text-gray-500 mt-1">1,234 views this week</div>
              </div>
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">Smart Watch Pro</div>
                <div className="text-xs text-gray-500 mt-1">987 views this week</div>
              </div>
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">Gaming Laptop</div>
                <div className="text-xs text-gray-500 mt-1">756 views this week</div>
              </div>
            </div>
          </div>

          {/* Latest Products Box */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Latest Arrivals
            </h3>
            <div className="space-y-3">
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">4K Ultra HD Camera</div>
                <div className="text-xs text-green-600 mt-1">Added 2 days ago</div>
              </div>
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">Mechanical Keyboard</div>
                <div className="text-xs text-green-600 mt-1">Added 3 days ago</div>
              </div>
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">Portable SSD 2TB</div>
                <div className="text-xs text-green-600 mt-1">Added 5 days ago</div>
              </div>
            </div>
          </div>

          {/* Most Reviewed Box */}
          <div className="bg-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
              <svg className="w-5 h-5 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
              </svg>
              Most Reviewed
            </h3>
            <div className="space-y-3">
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">Ergonomic Office Chair</div>
                <div className="flex items-center gap-1 mt-1">
                  <span className="text-yellow-500 text-xs">★★★★★</span>
                  <span className="text-xs text-gray-500">(342 reviews)</span>
                </div>
              </div>
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">Standing Desk</div>
                <div className="flex items-center gap-1 mt-1">
                  <span className="text-yellow-500 text-xs">★★★★☆</span>
                  <span className="text-xs text-gray-500">(287 reviews)</span>
                </div>
              </div>
              <div className="text-sm text-gray-600 p-3 bg-gray-50 rounded hover:bg-gray-100 transition-colors cursor-pointer">
                <div className="font-medium text-gray-900">LED Monitor 27"</div>
                <div className="flex items-center gap-1 mt-1">
                  <span className="text-yellow-500 text-xs">★★★★★</span>
                  <span className="text-xs text-gray-500">(256 reviews)</span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        {/* Main Content - Product Grid */}
        <main className="lg:col-span-3">
          {/* Active Filters Display */}
          {hasActiveFilters && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-blue-900">
                  {activeFilterCount > 0 && `${activeFilterCount} filter${activeFilterCount > 1 ? 's' : ''} applied`}
                  {filters.search && ` • Searching for "${filters.search}"`}
                </span>
                <button
                  onClick={handleClearFilters}
                  className="text-sm text-blue-600 hover:text-blue-800 transition-colors"
                >
                  Clear all
                </button>
              </div>
            </div>
          )}

          {/* Product Grid */}
          {productList.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {productList.map((product) => (
                <div
                  key={product.id}
                  className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow overflow-hidden flex flex-col"
                >
                  {/* Product Image */}
                  <Link href={`/products/${product.slug}`} className="block">
                    <div className="relative h-48 bg-gray-200">
                      {product.primary_image ? (
                        <img
                          src={product.primary_image}
                          alt={product.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="flex items-center justify-center h-full">
                          <span className="text-gray-400">No image</span>
                        </div>
                      )}
                      
                      {/* Stock Badge */}
                      {!product.is_available && (
                        <div className="absolute top-2 right-2 bg-red-600 text-white text-xs font-bold px-2 py-1 rounded">
                          OUT OF STOCK
                        </div>
                      )}
                      {product.is_available && product.is_low_stock && (
                        <div className="absolute top-2 right-2 bg-orange-500 text-white text-xs font-bold px-2 py-1 rounded">
                          LOW STOCK
                        </div>
                      )}
                    </div>
                  </Link>

                  {/* Product Info */}
                  <div className="p-4 flex-1 flex flex-col">
                    <Link href={`/products/${product.slug}`}>
                      <h3 className="text-lg font-semibold text-gray-800 hover:text-blue-600 transition-colors line-clamp-2 mb-2">
                        {product.name}
                      </h3>
                    </Link>

                    {product.category && (
                      <p className="text-xs text-gray-500 mb-2">
                        {product.category.name}
                      </p>
                    )}

                    <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                      {product.description}
                    </p>

                    {/* Rating */}
                    <div className="flex items-center gap-2 mb-3">
                      <div className="flex items-center">
                        <span className="text-yellow-500">★</span>
                        <span className="text-sm font-medium text-gray-700 ml-1">
                          {product.average_rating ? product.average_rating.toFixed(1) : 'N/A'}
                        </span>
                      </div>
                      <span className="text-xs text-gray-500">
                        ({product.review_count} reviews)
                      </span>
                    </div>

                    {/* Price */}
                    <p className="text-2xl font-bold text-gray-900 mb-4">
                      ${parseFloat(product.price).toFixed(2)}
                    </p>

                    {/* Actions */}
                    <div className="mt-auto space-y-2">
                      <Link
                        href={`/products/${product.slug}`}
                        className="block w-full text-center bg-gray-200 text-gray-900 py-2 px-4 rounded-lg hover:bg-gray-300 transition-colors font-medium"
                      >
                        View Details
                      </Link>
                      
                      <AddToCartButton 
                        product={product} 
                        variant="primary"
                        className="w-full"
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-24 w-24 text-gray-400 mb-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                No products found
              </h3>
              <p className="text-gray-600 mb-4">
                Try adjusting your filters or search terms
              </p>
              {hasActiveFilters && (
                <button
                  onClick={handleClearFilters}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Clear Filters
                </button>
              )}
            </div>
          )}

          {/* Pagination */}
          {products?.next && (
            <div className="mt-8 text-center">
              <button
                onClick={() => {
                  // Extract page from next URL
                  const url = new URL(products.next);
                  const page = url.searchParams.get('page');
                  setFilters({ ...filters, page });
                }}
                disabled={isLoading}
                className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-semibold"
              >
                {isLoading ? 'Loading...' : 'Load More Products'}
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default ProductsPage;