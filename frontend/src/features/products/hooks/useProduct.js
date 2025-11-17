import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getProducts, 
  getCategories, 
  getProductById,
  createProduct, 
  updateProduct, 
  deleteProduct,
  getMyProducts,
  bulkDeleteProducts,
  addProductImages,
  deleteProductImage
} from '../services/productService';

// Custom hook for fetching all products with optional filters
export const useProducts = (filters = {}) => {
  return useQuery({
    queryKey: ['products', filters],
    queryFn: () => getProducts(filters),
    staleTime: 2 * 60 * 1000, // 2 minutes
  });
};

// Custom hook for fetching categories
export const useCategories = () => {
  return useQuery({
    queryKey: ['categories'],
    queryFn: getCategories,
    staleTime: 10 * 60 * 1000, // 10 minutes - categories don't change often
  });
};

// Custom hook for fetching a single product by slug
export const useProductBySlug = (slug) => {
  // Fetch all products to map slug to id
  const { data: products, isLoading: isProductsLoading } = useQuery({
    queryKey: ['products'], 
    queryFn: getProducts,
    staleTime: 5 * 60 * 1000,
  });

  // Find the product by matching the slug
  const productsData = products?.results ?? [];
  const product = Array.isArray(productsData) 
    ? productsData.find((prod) => prod.slug === slug) 
    : null;

  // Use the ID to fetch the product details
  const { 
    data: detailedProductData,
    isLoading: isDetailLoading, 
    isError, 
    error 
  } = useQuery({
    queryKey: ['product', product?.id],
    queryFn: () => getProductById(product.id),
    enabled: !!product?.id,
  });

  // Combine loading states
  const isLoading = isProductsLoading || isDetailLoading;

  return { 
    product: detailedProductData, 
    isLoading, 
    isError, 
    error 
  };
};

// Custom hook for fetching a single product by ID directly
export const useProductById = (id) => {
  return useQuery({
    queryKey: ['product', id],
    queryFn: () => getProductById(id),
    enabled: !!id,
  });
};

// Custom hook for fetching seller's own products
export const useMyProducts = (filters = {}) => {
  return useQuery({
    queryKey: ['myProducts', filters],
    queryFn: () => getMyProducts(filters),
    staleTime: 1 * 60 * 1000, // 1 minute
  });
};

// Custom hook for creating a product
export const useCreateProduct = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createProduct,
    onSuccess: () => {
      // Invalidate product queries to refetch the data
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['myProducts'] });
    },
    onError: (error) => {
      console.error('Error creating product:', error);
    },
  });
};

// Custom hook for updating a product
export const useUpdateProduct = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, productData }) => updateProduct(id, productData),
    onSuccess: (data, variables) => {
      // Invalidate general product list
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['myProducts'] });
      
      // Update the single product query in the cache
      queryClient.setQueryData(['product', variables.id], data);
    },
    onError: (error) => {
      console.error('Error updating product:', error);
    },
  });
};

// Custom hook for deleting a product
export const useDeleteProduct = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deleteProduct,
    onSuccess: () => {
      // Invalidate product queries to refetch the data
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['myProducts'] });
    },
    onError: (error) => {
      console.error('Error deleting product:', error);
    },
  });
};

// Custom hook for bulk deleting products
export const useBulkDeleteProducts = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: bulkDeleteProducts,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] });
      queryClient.invalidateQueries({ queryKey: ['myProducts'] });
    },
    onError: (error) => {
      console.error('Error bulk deleting products:', error);
    },
  });
};

// Custom hook for adding images to a product
export const useAddProductImages = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ id, images }) => addProductImages(id, images),
    onSuccess: (data, variables) => {
      // Invalidate the specific product query
      queryClient.invalidateQueries({ queryKey: ['product', variables.id] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (error) => {
      console.error('Error adding product images:', error);
    },
  });
};

// Custom hook for deleting a product image
export const useDeleteProductImage = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ productId, imageId }) => deleteProductImage(productId, imageId),
    onSuccess: (data, variables) => {
      // Invalidate the specific product query
      queryClient.invalidateQueries({ queryKey: ['product', variables.productId] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (error) => {
      console.error('Error deleting product image:', error);
    },
  });
};