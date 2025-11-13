import api from '@/utils/api';

// Fetch reviews for a specific product
export const getReviewsForProduct = async (productId) => {
  try {
    const response = await api.get('/products/reviews/', {
      params: { product: productId }, // Filters reviews by product ID
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching reviews for product:', error);
    throw error;
  }
};

// Create a new review for a product (authenticated user)
export const createReview = async (reviewData) => {
  try {
    const response = await api.post('/products/reviews/', reviewData);
    return response.data;
  } catch (error) {
    console.error('Error creating review:', error);
    throw error;
  }
};

// Update an existing review (authenticated user)
export const updateReview = async (reviewId, reviewData) => {
  try {
    const response = await api.put(`/products/reviews/${reviewId}/`, reviewData);
    return response.data;
  } catch (error) {
    console.error('Error updating review:', error);
    throw error;
  }
};

// Mark a review as helpful (authenticated user)
export const voteHelpful = async (reviewId) => {
  try {
    const response = await api.post(`/products/reviews/${reviewId}/vote_helpful/`);
    return response.data;
  } catch (error) {
    console.error('Error voting for review:', error);
    throw error;
  }
};

// Create a reply to a review (authenticated user)
export const createReply = async (reviewId, replyData) => {
  try {
    const response = await api.post('/products/replies/', { ...replyData, review: reviewId });
    return response.data;
  } catch (error) {
    console.error('Error creating reply:', error);
    throw error;
  }
};

// Update a review reply (authenticated user)
export const updateReply = async (replyId, replyData) => {
  try {
    const response = await api.put(`/products/replies/${replyId}/`, replyData);
    return response.data;
  } catch (error) {
    console.error('Error updating reply:', error);
    throw error;
  }
};

// Delete a review reply (authenticated user)
export const deleteReply = async (replyId) => {
  try {
    const response = await api.delete(`/products/replies/${replyId}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting reply:', error);
    throw error;
  }
};
