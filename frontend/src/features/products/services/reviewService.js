import api from '@/utils/api';

// Fetch reviews for a specific product
export const getReviewsForProduct = async (productId) => {
  try {
    const response = await api.get('/products/reviews/', {
      params: { product: productId }, // Filters reviews by product ID
    });
    // Backend doesn't wrap list response
    return response.data;
  } catch (error) {
    console.error('Error fetching reviews for product:', error);
    throw error;
  }
};

// Create a new review for a product (authenticated user)
export const createReview = async (reviewData) => {
  try {
    // Support image upload
    const formData = new FormData();
    formData.append('product', reviewData.product);
    formData.append('rating', reviewData.rating);
    if (reviewData.title) formData.append('title', reviewData.title);
    if (reviewData.content) formData.append('content', reviewData.content);
    if (reviewData.image) formData.append('image', reviewData.image);

    const response = await api.post('/products/reviews/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Backend wraps response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error creating review:', error);
    throw error;
  }
};

// Update an existing review (authenticated user)
export const updateReview = async (reviewId, reviewData) => {
  try {
    const formData = new FormData();
    if (reviewData.rating) formData.append('rating', reviewData.rating);
    if (reviewData.title) formData.append('title', reviewData.title);
    if (reviewData.content) formData.append('content', reviewData.content);
    if (reviewData.image) formData.append('image', reviewData.image);

    const response = await api.patch(`/products/reviews/${reviewId}/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    // Backend wraps response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error updating review:', error);
    throw error;
  }
};

// Delete a review (authenticated user)
export const deleteReview = async (reviewId) => {
  try {
    const response = await api.delete(`/products/reviews/${reviewId}/`);
    return response.data;
  } catch (error) {
    console.error('Error deleting review:', error);
    throw error;
  }
};

// Mark a review as helpful (authenticated user) - toggles on/off
export const voteHelpful = async (reviewId) => {
  try {
    const response = await api.post(`/products/reviews/${reviewId}/vote_helpful/`);
    // Backend wraps response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error voting for review:', error);
    throw error;
  }
};

// Create a reply to a review (authenticated seller only)
export const createReply = async (reviewId, replyData) => {
  try {
    const response = await api.post('/products/replies/', { 
      ...replyData, 
      review: reviewId 
    });
    
    // Backend wraps response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
  } catch (error) {
    console.error('Error creating reply:', error);
    throw error;
  }
};

// Update a review reply (authenticated user)
export const updateReply = async (replyId, replyData) => {
  try {
    const response = await api.patch(`/products/replies/${replyId}/`, replyData);
    // Backend wraps response in {success, message, data}
    return response.data.success ? response.data.data : response.data;
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