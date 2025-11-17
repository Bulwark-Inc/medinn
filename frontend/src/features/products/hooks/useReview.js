import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
    getReviewsForProduct, 
    createReview, 
    updateReview,
    deleteReview,
    voteHelpful, 
    createReply, 
    updateReply, 
    deleteReply 
} from '../services/reviewService';

// Custom hook for fetching reviews for a specific product by ID
export const useReviews = (productId, options = {}) => {
  return useQuery({
    queryKey: ['reviews', productId], 
    queryFn: () => getReviewsForProduct(productId),
    enabled: !!productId && (options.enabled ?? true),
    staleTime: 1 * 60 * 1000, // 1 minute
    ...options
  });
};

// Custom hook for creating a review
export const useCreateReview = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createReview,
    onSuccess: (newReview) => {
      // Invalidate the reviews for the specific product ID to refetch
      queryClient.invalidateQueries({ queryKey: ['reviews', newReview.product] });
      
      // Also invalidate the main product detail which contains the rating
      queryClient.invalidateQueries({ queryKey: ['product', newReview.product] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (error) => {
      console.error('Error creating review:', error);
    },
  });
};

// Custom hook for updating a review
export const useUpdateReview = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: ({ reviewId, reviewData }) => updateReview(reviewId, reviewData),
    onSuccess: (updatedReview) => {
      // Invalidate the reviews for the specific product ID to refetch
      queryClient.invalidateQueries({ queryKey: ['reviews', updatedReview.product] });
      queryClient.invalidateQueries({ queryKey: ['product', updatedReview.product] });
    },
    onError: (error) => {
      console.error('Error updating review:', error);
    },
  });
};

// Custom hook for deleting a review
export const useDeleteReview = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: deleteReview,
    onSuccess: () => {
      // Invalidate all reviews queries
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
      queryClient.invalidateQueries({ queryKey: ['products'] });
    },
    onError: (error) => {
      console.error('Error deleting review:', error);
    },
  });
};

// Custom hook for marking a review as helpful (toggles)
export const useVoteHelpful = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: voteHelpful,
    onSuccess: () => {
      // Invalidate the list of reviews to show the updated helpful count
      queryClient.invalidateQueries({ queryKey: ['reviews'] });
    },
    onError: (error) => {
      console.error('Error voting for review:', error);
    },
  });
};

// Custom hook for creating a reply to a review
export const useCreateReply = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ reviewId, replyData }) => createReply(reviewId, replyData),
    onSuccess: () => {
      // Invalidate the reviews to show the new reply (since replies are nested in reviews)
      queryClient.invalidateQueries({ queryKey: ['reviews'] }); 
    },
    onError: (error) => {
      console.error('Error creating reply:', error);
    },
  });
};

// Custom hook for updating a review reply
export const useUpdateReply = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({ replyId, replyData }) => updateReply(replyId, replyData),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] }); // Invalidate reviews to update the nested reply
    },
    onError: (error) => {
      console.error('Error updating reply:', error);
    },
  });
};

// Custom hook for deleting a review reply
export const useDeleteReply = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: deleteReply,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reviews'] }); // Invalidate reviews to remove the nested reply
    },
    onError: (error) => {
      console.error('Error deleting reply:', error);
    },
  });
};