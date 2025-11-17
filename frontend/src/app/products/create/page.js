"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useCreateProduct, useCategories } from "@/features/products/hooks/useProduct"; 

export default function CreateProductPage() {
  const router = useRouter();
  const { mutate: createProduct, isPending, isError, error } = useCreateProduct();
  const { data: categories, isLoading: isCategoriesLoading } = useCategories();
  
  const [productData, setProductData] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
    category_id: '',
    low_stock_threshold: '10',
    is_active: true,
  });
  
  const [images, setImages] = useState([]);
  const [imagePreviews, setImagePreviews] = useState([]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setProductData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleImageChange = (e) => {
    const files = Array.from(e.target.files);
    
    if (files.length + images.length > 10) {
      alert('Maximum 10 images allowed');
      return;
    }

    // Validate file sizes (5MB max each)
    const oversizedFiles = files.filter(file => file.size > 5 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      alert('Some images exceed 5MB. Please choose smaller files.');
      return;
    }

    setImages(prev => [...prev, ...files]);

    // Create previews
    files.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreviews(prev => [...prev, reader.result]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeImage = (index) => {
    setImages(prev => prev.filter((_, i) => i !== index));
    setImagePreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validation
    if (!productData.name || !productData.price || !productData.stock) {
      alert('Please fill in all required fields');
      return;
    }

    if (parseFloat(productData.price) <= 0) {
      alert('Price must be greater than 0');
      return;
    }

    if (parseInt(productData.stock) < 0) {
      alert('Stock cannot be negative');
      return;
    }

    // Prepare data
    const submitData = {
      ...productData,
      price: parseFloat(productData.price),
      stock: parseInt(productData.stock),
      low_stock_threshold: parseInt(productData.low_stock_threshold),
      images: images,
    };

    createProduct(submitData, {
      onSuccess: (newProduct) => {
        alert(`Product "${newProduct.name}" created successfully!`);
        router.push(`/products/${newProduct.slug}`); 
      },
      onError: (err) => {
        const errorMessage = err.response?.data?.message || 
                            err.response?.data?.errors?.name?.[0] ||
                            'Failed to create product';
        alert(errorMessage);
      }
    });
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Create New Product</h1>
      
      {isError && (
        <div className="p-4 mb-4 bg-red-100 text-red-700 rounded-lg">
          <p className="font-semibold">Error creating product</p>
          <p className="text-sm">{error?.message || 'Please try again'}</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow-md">
        {/* Basic Information */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 border-b pb-2">
            Basic Information
          </h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Product Name *
            </label>
            <input
              type="text"
              name="name"
              value={productData.name}
              onChange={handleChange}
              required
              maxLength={255}
              className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Enter product name"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description *
            </label>
            <textarea
              name="description"
              value={productData.description}
              onChange={handleChange}
              required
              rows={5}
              className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Describe your product..."
            />
          </div>
        </div>

        {/* Category */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          {isCategoriesLoading ? (
            <div className="text-sm text-gray-500">Loading categories...</div>
          ) : (
            <select
              name="category_id"
              value={productData.category_id}
              onChange={handleChange}
              className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Select a category (optional)</option>
              {Array.isArray(categories) && categories.map((category) => (
                <option key={category.id} value={category.id}>
                  {category.name}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Pricing & Stock */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 border-b pb-2">
            Pricing & Inventory
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Price ($) *
              </label>
              <input
                type="number"
                name="price"
                min="0.01"
                step="0.01"
                value={productData.price}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Stock Quantity *
              </label>
              <input
                type="number"
                name="stock"
                min="0"
                value={productData.stock}
                onChange={handleChange}
                required
                className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Low Stock Threshold
              </label>
              <input
                type="number"
                name="low_stock_threshold"
                min="0"
                value={productData.low_stock_threshold}
                onChange={handleChange}
                className="w-full border border-gray-300 p-3 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <p className="text-xs text-gray-500 mt-1">
                Alert when stock falls below this number
              </p>
            </div>

            <div className="flex items-center">
              <label className="flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  name="is_active"
                  checked={productData.is_active}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                />
                <span className="ml-2 text-sm font-medium text-gray-700">
                  Active (visible to buyers)
                </span>
              </label>
            </div>
          </div>
        </div>

        {/* Images */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 border-b pb-2">
            Product Images
          </h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Images (Max 10, 5MB each)
            </label>
            <input
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              multiple
              onChange={handleImageChange}
              className="w-full border border-gray-300 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Accepted formats: JPEG, PNG, WebP. First image will be the primary image.
            </p>
          </div>

          {/* Image Previews */}
          {imagePreviews.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {imagePreviews.map((preview, index) => (
                <div key={index} className="relative">
                  <img
                    src={preview}
                    alt={`Preview ${index + 1}`}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  {index === 0 && (
                    <span className="absolute top-1 left-1 bg-blue-600 text-white text-xs px-2 py-1 rounded">
                      Primary
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute top-1 right-1 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-700"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit Button */}
        <div className="flex gap-4 pt-4">
          <button
            type="submit"
            disabled={isPending}
            className={`flex-1 py-3 rounded-lg text-white font-semibold transition-colors ${
              isPending 
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isPending ? 'Creating Product...' : 'Create Product'}
          </button>
          
          <button
            type="button"
            onClick={() => router.back()}
            className="px-6 py-3 rounded-lg bg-gray-200 text-gray-700 font-semibold hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </form>
    </div>
  );
}