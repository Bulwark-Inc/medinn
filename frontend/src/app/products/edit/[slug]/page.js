"use client";

import { useParams, useRouter } from 'next/navigation';
import { useState, useEffect } from 'react';
import { 
  useProductBySlug, 
  useUpdateProduct,
  useCategories,
  useAddProductImages,
  useDeleteProductImage
} from "@/features/products/hooks/useProduct"; 

export default function UpdateProductPage() {
  const router = useRouter();
  const params = useParams();
  const slug = params.slug; 

  const { 
    product: initialData, 
    isLoading: isFetching, 
    isError: fetchError 
  } = useProductBySlug(slug);

  const { mutate: updateProduct, isPending: isUpdating } = useUpdateProduct();
  const { data: categories, isLoading: isCategoriesLoading } = useCategories();
  const { mutate: addImages, isPending: isAddingImages } = useAddProductImages();
  const { mutate: deleteImage } = useDeleteProductImage();

  const [productData, setProductData] = useState({
    name: '',
    description: '',
    price: '',
    stock: '',
    category_id: '',
    low_stock_threshold: '10',
    is_active: true,
  });
  
  const [newImages, setNewImages] = useState([]);
  const [newImagePreviews, setNewImagePreviews] = useState([]);

  // Populate state when initial data arrives
  useEffect(() => {
    if (initialData) {
      setProductData({
        name: initialData.name || '',
        description: initialData.description || '',
        price: initialData.price || '',
        stock: initialData.stock || '',
        category_id: initialData.category?.id || '',
        low_stock_threshold: initialData.low_stock_threshold || '10',
        is_active: initialData.is_active ?? true,
      });
    }
  }, [initialData]);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setProductData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleNewImageChange = (e) => {
    const files = Array.from(e.target.files);
    
    const currentImageCount = initialData?.images?.length || 0;
    const totalImages = currentImageCount + newImages.length + files.length;
    
    if (totalImages > 10) {
      alert('Maximum 10 images allowed per product');
      return;
    }

    // Validate file sizes (5MB max each)
    const oversizedFiles = files.filter(file => file.size > 5 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      alert('Some images exceed 5MB. Please choose smaller files.');
      return;
    }

    setNewImages(prev => [...prev, ...files]);

    // Create previews
    files.forEach(file => {
      const reader = new FileReader();
      reader.onloadend = () => {
        setNewImagePreviews(prev => [...prev, reader.result]);
      };
      reader.readAsDataURL(file);
    });
  };

  const removeNewImage = (index) => {
    setNewImages(prev => prev.filter((_, i) => i !== index));
    setNewImagePreviews(prev => prev.filter((_, i) => i !== index));
  };

  const handleDeleteExistingImage = (imageId) => {
    if (window.confirm('Are you sure you want to delete this image?')) {
      deleteImage(
        { productId: initialData.id, imageId },
        {
          onSuccess: () => {
            alert('Image deleted successfully');
          },
          onError: (err) => {
            alert(err.response?.data?.message || 'Failed to delete image');
          }
        }
      );
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!initialData?.id) {
      alert("Error: Product ID not found for update.");
      return;
    }

    // Validation
    if (productData.price && parseFloat(productData.price) <= 0) {
      alert('Price must be greater than 0');
      return;
    }

    if (productData.stock && parseInt(productData.stock) < 0) {
      alert('Stock cannot be negative');
      return;
    }

    // Prepare update data (only changed fields)
    const updateData = {
      ...productData,
      price: productData.price ? parseFloat(productData.price) : undefined,
      stock: productData.stock ? parseInt(productData.stock) : undefined,
      low_stock_threshold: productData.low_stock_threshold 
        ? parseInt(productData.low_stock_threshold) 
        : undefined,
    };

    // Remove undefined values
    Object.keys(updateData).forEach(key => 
      updateData[key] === undefined && delete updateData[key]
    );
    
    updateProduct(
      { id: initialData.id, productData: updateData }, 
      {
        onSuccess: () => {
          // If there are new images, add them
          if (newImages.length > 0) {
            addImages(
              { id: initialData.id, images: newImages },
              {
                onSuccess: () => {
                  alert(`Product "${productData.name}" updated successfully with new images!`);
                  router.push(`/products/${slug}`);
                },
                onError: (err) => {
                  alert('Product updated but failed to add images: ' + 
                        (err.response?.data?.message || 'Unknown error'));
                  router.push(`/products/${slug}`);
                }
              }
            );
          } else {
            alert(`Product "${productData.name}" updated successfully!`);
            router.push(`/products/${slug}`);
          }
        },
        onError: (err) => {
          alert(err.response?.data?.message || 'Failed to update product');
        }
      }
    );
  };

  // Loading state
  if (isFetching) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
          <p className="text-gray-600">Loading product data...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (fetchError || !initialData) {
    return (
      <div className="max-w-3xl mx-auto p-6">
        <div className="text-center py-12">
          <p className="text-red-600 text-lg mb-4">Error: Could not load product for editing.</p>
          <button
            onClick={() => router.back()}
            className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6">
      <h1 className="text-3xl font-bold mb-2">Update Product</h1>
      <p className="text-gray-600 mb-6">{initialData.name}</p>

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

        {/* Existing Images */}
        {initialData.images && initialData.images.length > 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-semibold text-gray-900 border-b pb-2">
              Current Images
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {initialData.images.map((img) => (
                <div key={img.id} className="relative">
                  <img
                    src={img.image}
                    alt={img.alt_text || 'Product image'}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  {img.is_primary && (
                    <span className="absolute top-1 left-1 bg-blue-600 text-white text-xs px-2 py-1 rounded">
                      Primary
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={() => handleDeleteExistingImage(img.id)}
                    className="absolute top-1 right-1 bg-red-600 text-white rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-700"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Add New Images */}
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 border-b pb-2">
            Add New Images
          </h2>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Additional Images
            </label>
            <input
              type="file"
              accept="image/jpeg,image/jpg,image/png,image/webp"
              multiple
              onChange={handleNewImageChange}
              className="w-full border border-gray-300 p-2 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p className="text-xs text-gray-500 mt-1">
              Max 10 total images per product. Each image max 5MB.
            </p>
          </div>

          {/* New Image Previews */}
          {newImagePreviews.length > 0 && (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {newImagePreviews.map((preview, index) => (
                <div key={index} className="relative">
                  <img
                    src={preview}
                    alt={`New image ${index + 1}`}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  <span className="absolute top-1 left-1 bg-green-600 text-white text-xs px-2 py-1 rounded">
                    New
                  </span>
                  <button
                    type="button"
                    onClick={() => removeNewImage(index)}
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
            disabled={isUpdating || isAddingImages}
            className={`flex-1 py-3 rounded-lg text-white font-semibold transition-colors ${
              isUpdating || isAddingImages
                ? 'bg-gray-400 cursor-not-allowed' 
                : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {isUpdating || isAddingImages ? 'Updating...' : 'Update Product'}
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