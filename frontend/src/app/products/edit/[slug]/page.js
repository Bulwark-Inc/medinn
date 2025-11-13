"use client";

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
// Import the existing fetching hook and the update hook
import { useProductBySlug, useUpdateProduct } from "@/features/products/hooks/useProduct"; 
// Note: You must ensure useUpdateProduct is imported correctly from your hook file.

export default function UpdateProductPage() {
  const router = useRouter();
  const params = useParams();
  // 1. Get the 'slug' from the URL parameters
  const slug = params.slug; 

  // 2. Use the slug-based hook to fetch the existing product data
  const { 
    product: initialData, // Renamed data to initialData for clarity
    isLoading: isFetching, 
    isError: fetchError 
  } = useProductBySlug(slug);

  // Get the mutation function and states
  const { mutate: updateProduct, isLoading: isUpdating, isError: updateError } = useUpdateProduct();

  const [productData, setProductData] = useState({
    // Initialize with placeholders; will be populated in useEffect
    name: '',
    description: '',
    price: 0,
    stock: 0,
    category: '',
    image: '',
  });

  // 3. Populate state when initial data arrives
  useEffect(() => {
    if (initialData) {
      setProductData({
        name: initialData.name || '',
        description: initialData.description || '',
        price: initialData.price || 0,
        stock: initialData.stock || 0,
        // Assuming category is stored as an ID or name you want to edit
        category: initialData.category || '', 
        image: initialData.image || '',
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setProductData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!initialData?.id) {
      alert("Error: Product ID not found for update.");
      return;
    }
    
    // Pass the product's ID (derived from the fetched data) and the updated data
    updateProduct({ id: initialData.id, productData: productData }, {
      onSuccess: () => {
        alert(`Product "${productData.name}" updated successfully!`);
        // Redirect back to the product detail page, using the slug
        router.push(`/products/${slug}`); 
      },
    });
  };

  // --- UI Logic ---
  if (isFetching) return <p className="p-6 text-center">Loading product data...</p>;
  if (fetchError || !initialData) return <p className="p-6 text-center text-red-600">Error: Could not load product for editing.</p>;

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Update Product: {initialData.name}</h1>
      
      {updateError && (
        <p className="p-3 mb-4 bg-red-100 text-red-700 rounded">
          Error: Failed to update product. {updateError.message}
        </p>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Name</label>
          <input
            type="text"
            name="name"
            value={productData.name}
            onChange={handleChange}
            required
            className="w-full border p-2 rounded"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Description</label>
          <textarea
            name="description"
            value={productData.description}
            onChange={handleChange}
            required
            className="w-full border p-2 rounded h-24"
          />
        </div>
        
        <div className="flex space-x-4">
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Price ($)</label>
            <input
              type="number"
              name="price"
              min="0.01"
              step="0.01"
              value={productData.price}
              onChange={handleChange}
              required
              className="w-full border p-2 rounded"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium mb-1">Stock</label>
            <input
              type="number"
              name="stock"
              min="0"
              value={productData.stock}
              onChange={handleChange}
              required
              className="w-full border p-2 rounded"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Category (ID/Slug)</label>
          <input
            type="text"
            name="category"
            value={productData.category}
            onChange={handleChange}
            required
            className="w-full border p-2 rounded"
          />
        </div>

        <button
          type="submit"
          disabled={isUpdating}
          className={`w-full py-2 rounded text-white font-semibold ${
            isUpdating ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isUpdating ? 'Updating...' : 'Update Product'}
        </button>
      </form>
    </div>
  );
}