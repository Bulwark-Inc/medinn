import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { 
    getReviewsForProduct, 
    createReview, 
    updateReview, 
    voteHelpful, 
    createReply, 
    updateReply, 
    deleteReply 
} from '../services/reviewService';

// Custom hook for fetching reviews for a specific product by ID
// The parameter is changed from 'slug' to 'productId'
export const useReviews = (productId, options = {}) => {
  return useQuery({
    queryKey: ['reviews', productId], 
    queryFn: () => getReviewsForProduct(productId),
    // Ensure the query only runs when the productId is truthy (i.e., we have the ID)
    enabled: !!productId && (options.enabled ?? true), 
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
      
      // OPTIONAL: Also invalidate the main product detail which contains the rating
      queryClient.invalidateQueries({ queryKey: ['product', newReview.product] });
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
    mutationFn: updateReview,
    onSuccess: (updatedReview) => {
      // Invalidate the reviews for the specific product ID to refetch
      queryClient.invalidateQueries({ queryKey: ['reviews', updatedReview.product] });
    },
    onError: (error) => {
      console.error('Error updating review:', error);
    },
  });
};

// Custom hook for marking a review as helpful
export const useVoteHelpful = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: voteHelpful,
    onSuccess: (votedReview) => {
      // Optimistically update the single review in the cache (if fetched by ID)
      queryClient.setQueryData(['review', votedReview.id], votedReview);
      
      // Invalidate the list of reviews to show the updated helpful count in the list
      // Note: Since 'votedReview' doesn't return the product ID in your provided code,
      // a general 'reviews' invalidation might be needed unless you modify the API.
      // Assuming a blanket invalidation is safe for now:
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
    mutationFn: (data) => createReply(data.reviewId, data.replyData), // Destructure args
    onSuccess: (newReply) => {
      // Invalidate the reviews to show the new reply (since replies are nested in reviews)
      // Note: We need the product ID associated with the review to invalidate efficiently.
      // For now, let's stick to a general invalidation on the review list.
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
    mutationFn: updateReply,
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