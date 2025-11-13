import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
  getProducts, 
  getCategories, 
  getProductById,
  createProduct, 
  updateProduct, 
  deleteProduct 
} from '../services/productService';


// Custom hook for fetching all products with optional filters
export const useProducts = (filters = {}) => {
  return useQuery(
    {
      queryKey: ['products', filters],
      queryFn: () => getProducts(filters),
      keepPreviousData: true,
    }
  );
};


// Custom hook for fetching categories
export const useCategories = () => {
  return useQuery(
    {
      queryKey: ['categories'],
      queryFn: () => getCategories(),
      keepPreviousData: true,
    }
  );
};


// Custom hook for fetching a single product by slug
export const useProductBySlug = (slug) => {
  // 1. Fetch all products to map slug to id
  const { data: products, isLoading: isProductsLoading } = useQuery(
    {
      queryKey: ['products'], 
      queryFn: getProducts,
      staleTime: 5 * 60 * 1000,
    }
  );

  // 2. Find the product by matching the slug
  const product = products?.find((prod) => prod.slug === slug);

  // 3. Use the ID to fetch the product details
  const { 
    data: detailedProductData,
    isLoading: isDetailLoading, 
    isError, 
    error 
  } = useQuery(
    {
      queryKey: ['product', product?.id],
      queryFn: () => getProductById(product.id),
      enabled: !!product,
    }
  );

  // Combine loading states for the consumer
  const isLoading = isProductsLoading || isDetailLoading;

  // Return the necessary state
  return { 
    product: detailedProductData, 
    isLoading, 
    isError, 
    error 
  };
};


// Custom hook for creating a product
export const useCreateProduct = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: createProduct,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['products'] }); // Invalidate product queries to refetch the data
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
    mutationFn: updateProduct,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['products'] }); // Invalidate general product list
      // Optional: Update the single product query in the cache
      queryClient.setQueryData(['product', data.id], data); 
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
      queryClient.invalidateQueries({ queryKey: ['products'] }); // Invalidate product queries to refetch the data
    },
    onError: (error) => {
      console.error('Error deleting product:', error);
    },
  });
};