"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateProduct, useCategories } from "@/features/products/hooks/useProduct"; 

export default function CreateProductPage() {
  const router = useRouter();
  const { mutate: createProduct, isLoading, isError, error } = useCreateProduct();
  const { data: categories, isLoading: isCategoriesLoading, error: categoriesError } = useCategories();
  
  const [productData, setProductData] = useState({
    name: '',
    description: '',
    price: 0,
    stock: 1,
    category: '', // Assuming category is an ID or slug
    image: 'https://via.placeholder.com/400', // Default placeholder image
  });

  const handleChange = (e) => {
    const { name, value, type } = e.target;
    setProductData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    createProduct(productData, {
      onSuccess: (newProduct) => {
        // Redirect to the newly created product's detail page (using slug or ID if available)
        alert(`Product "${newProduct.name}" created successfully!`);
        // Assuming your backend returns a slug, otherwise use ID
        router.push(`/products/${newProduct.slug || newProduct.id}`); 
      },
    });
  };

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Create New Product</h1>
      
      {isError && (
        <p className="p-3 mb-4 bg-red-100 text-red-700 rounded">
          Error: Failed to create product. {error.message}
        </p>
      )}
      
      {categoriesError && (
        <p className="p-3 mb-4 bg-red-100 text-red-700 rounded">
          Error loading categories. {error.message}
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
          <label className="block text-sm font-medium mb-1">Category</label>
          {isCategoriesLoading ? (
            <div className="text-sm text-gray-500">Loading...</div>
          ) : (
            <select
              name="category"
              value={productData.category}
              onChange={handleChange}
              required
              className="w-full border p-2 rounded"
            >
              <option value="" disabled>Select a category</option>
              {categories?.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          )}
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className={`w-full py-2 rounded text-white font-semibold ${
            isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {isLoading ? 'Creating...' : 'Create Product'}
        </button>
      </form>
    </div>
  );
}