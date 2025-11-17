"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { useProductBySlug } from "@/features/products/hooks/useProduct"; 
import { 
  useReviews, 
  useCreateReview, 
  useVoteHelpful,
  useCreateReply
} from "@/features/products/hooks/useReview";
import { useState } from "react";
import AddToCartButton from '@/features/cart/components/AddToCartButton';
import { useAuth } from '@/contexts/AuthContext';

export default function ProductDetail() {
  const params = useParams();
  const slug = params.slug; 
  const { user } = useAuth();

  const { 
    product, 
    isLoading,
    isError,
    error
  } = useProductBySlug(slug);

  const productId = product?.id; 

  // Fetch reviews conditionally
  const { data: reviewsData, isLoading: reviewsLoading } = useReviews(productId, { 
    enabled: !!productId 
  });
  
  // Extract reviews array from response
  const reviews = reviewsData?.results || reviewsData || [];
  
  const createReview = useCreateReview();
  const voteHelpful = useVoteHelpful(); 
  const createReply = useCreateReply();
  
  const [review, setReview] = useState({ 
    rating: 5, 
    title: "",
    content: "" 
  });
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [replyingTo, setReplyingTo] = useState(null);
  const [replyContent, setReplyContent] = useState("");

  // Handle Loading State
  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="text-center">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mb-4"></div>
            <p className="text-gray-600">Loading product details...</p>
          </div>
        </div>
      </div>
    );
  }

  // Handle Error State
  if (isError || !product) {
    return (
      <div className="container mx-auto px-4 py-12">
        <div className="text-center">
          <svg
            className="mx-auto h-24 w-24 text-red-400 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Product Not Found
          </h2>
          <p className="text-gray-600 mb-6">
            {error?.message || "The product you're looking for doesn't exist or has been removed."}
          </p>
          <Link
            href="/products"
            className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-semibold"
          >
            Browse All Products
          </Link>
        </div>
      </div>
    );
  }

  // Handle Review Submission
  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    
    if (!user) {
      alert('Please login to submit a review');
      return;
    }

    if (!review.content.trim()) {
      alert('Please write a review');
      return;
    }

    try {
      await createReview.mutateAsync({ 
        product: product.id, 
        ...review 
      });
      
      // Reset form and hide it
      setReview({ rating: 5, title: "", content: "" });
      setShowReviewForm(false);
    } catch (error) {
      console.error('Failed to submit review:', error);
      const errorMessage = error.response?.data?.message || 
                          error.response?.data?.errors?.non_field_errors?.[0] ||
                          'Failed to submit review. You may have already reviewed this product.';
      alert(errorMessage);
    }
  };

  // Handle Reply Submission
  const handleReplySubmit = async (reviewId) => {
    if (!user) {
      alert('Please login to reply');
      return;
    }

    if (!replyContent.trim()) {
      alert('Please write a reply');
      return;
    }

    try {
      await createReply.mutateAsync({
        reviewId,
        replyData: { content: replyContent }
      });
      
      setReplyingTo(null);
      setReplyContent("");
    } catch (error) {
      console.error('Failed to submit reply:', error);
      const errorMessage = error.response?.data?.message || 
                          'Failed to submit reply. Only the seller can reply to reviews.';
      alert(errorMessage);
    }
  };

  // Render star rating
  const renderStars = (rating) => {
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={`text-xl ${
              star <= rating ? 'text-yellow-500' : 'text-gray-300'
            }`}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  // Get primary image or first image
  const primaryImage = product.images?.find(img => img.is_primary)?.image || 
                       product.images?.[0]?.image;

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="text-sm text-gray-600 mb-6">
        <Link href="/" className="hover:text-blue-600">Home</Link>
        <span className="mx-2">/</span>
        <Link href="/products" className="hover:text-blue-600">Products</Link>
        <span className="mx-2">/</span>
        {product.category && (
          <>
            <span>{product.category.name}</span>
            <span className="mx-2">/</span>
          </>
        )}
        <span className="text-gray-900">{product.name}</span>
      </nav>

      {/* Product Details Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
        {/* Product Images */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {/* Main Image */}
          {primaryImage ? (
            <img 
              src={primaryImage} 
              alt={product.name} 
              className="w-full h-auto rounded-lg object-contain max-h-[500px] mb-4"
            />
          ) : (
            <div className="w-full h-96 bg-gray-200 rounded-lg flex items-center justify-center mb-4">
              <span className="text-gray-400 text-lg">No image available</span>
            </div>
          )}

          {/* Image Gallery */}
          {product.images && product.images.length > 1 && (
            <div className="grid grid-cols-4 gap-2">
              {product.images.map((img, index) => (
                <img
                  key={img.id}
                  src={img.image}
                  alt={img.alt_text || `${product.name} ${index + 1}`}
                  className="w-full h-20 object-cover rounded cursor-pointer hover:opacity-75 transition-opacity"
                />
              ))}
            </div>
          )}
        </div>

        {/* Product Info */}
        <div className="bg-white rounded-lg shadow-md p-6">
          {/* Category */}
          {product.category && (
            <p className="text-sm text-blue-600 font-medium mb-2">
              {product.category.name}
            </p>
          )}

          {/* Product Name */}
          <h1 className="text-3xl font-bold text-gray-900 mb-4">
            {product.name}
          </h1>

          {/* Rating */}
          <div className="flex items-center gap-3 mb-4">
            {renderStars(Math.round(product.average_rating || 0))}
            <span className="text-sm text-gray-600">
              {product.average_rating ? product.average_rating.toFixed(1) : 'No ratings yet'}
            </span>
            <span className="text-sm text-gray-500">
              ({product.review_count} reviews)
            </span>
          </div>

          {/* Price */}
          <div className="mb-6">
            <p className="text-4xl font-bold text-gray-900">
              ${parseFloat(product.price).toFixed(2)}
            </p>
          </div>

          {/* Stock Status */}
          <div className="mb-6">
            {product.is_available ? (
              <>
                <p className="text-green-600 font-medium">
                  ✓ In Stock ({product.stock} available)
                </p>
                {product.is_low_stock && (
                  <p className="text-orange-600 text-sm mt-1">
                    ⚠ Low stock - order soon!
                  </p>
                )}
              </>
            ) : (
              <p className="text-red-600 font-medium">
                ✗ Out of Stock
              </p>
            )}
          </div>

          {/* Seller Info */}
          {product.seller && (
            <div className="mb-6 p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-600">
                Sold by: <span className="font-semibold text-gray-900">{product.seller}</span>
              </p>
            </div>
          )}

          {/* Add to Cart */}
          <div className="mb-6">
            <AddToCartButton 
              product={product} 
              showQuantitySelector={true}
              variant="primary"
            />
          </div>

          {/* Description */}
          <div className="border-t border-gray-200 pt-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">
              Product Description
            </h2>
            <p className="text-gray-700 leading-relaxed whitespace-pre-line">
              {product.description || 'No description available.'}
            </p>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            Customer Reviews ({product.review_count})
          </h2>
          
          {user && !showReviewForm && (
            <button
              onClick={() => setShowReviewForm(true)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              Write a Review
            </button>
          )}
        </div>

        {/* Review Form */}
        {showReviewForm && (
          <form onSubmit={handleReviewSubmit} className="mb-8 border border-gray-200 rounded-lg p-6 bg-gray-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Write Your Review</h3>
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            {/* Rating Selection */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Rating *
              </label>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setReview({ ...review, rating: star })}
                    className="text-3xl transition-colors"
                  >
                    <span className={star <= review.rating ? 'text-yellow-500' : 'text-gray-300'}>
                      ★
                    </span>
                  </button>
                ))}
              </div>
            </div>

            {/* Review Title */}
            <div className="mb-4">
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Review Title
              </label>
              <input
                id="title"
                type="text"
                value={review.title}
                onChange={(e) => setReview({ ...review, title: e.target.value })}
                placeholder="Summarize your experience"
                maxLength={255}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Review Content */}
            <div className="mb-4">
              <label htmlFor="content" className="block text-sm font-medium text-gray-700 mb-2">
                Your Review *
              </label>
              <textarea
                id="content"
                value={review.content}
                onChange={(e) => setReview({ ...review, content: e.target.value })}
                placeholder="Share your thoughts about this product..."
                rows={5}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {/* Submit Button */}
            <div className="flex gap-3">
              <button
                type="submit"
                disabled={createReview.isPending}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
              >
                {createReview.isPending ? 'Submitting...' : 'Submit Review'}
              </button>
              <button
                type="button"
                onClick={() => setShowReviewForm(false)}
                className="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {/* Reviews List */}
        {reviewsLoading ? (
          <div className="text-center py-8">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <p className="text-gray-600 mt-2">Loading reviews...</p>
          </div>
        ) : reviews && reviews.length > 0 ? (
          <div className="space-y-6">
            {reviews.map((r) => (
              <div key={r.id} className="border-b border-gray-200 pb-6 last:border-0">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <p className="font-semibold text-gray-900">{r.user}</p>
                      {r.is_verified && (
                        <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          Verified Purchase
                        </span>
                      )}
                    </div>
                    <div className="flex items-center gap-2">
                      {renderStars(r.rating)}
                      <span className="text-sm text-gray-500">
                        {new Date(r.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                </div>

                {r.title && (
                  <h4 className="font-semibold text-gray-900 mb-2">{r.title}</h4>
                )}

                <p className="text-gray-700 mb-3 whitespace-pre-line">{r.content}</p>

                {r.image && (
                  <img 
                    src={r.image} 
                    alt="Review" 
                    className="w-48 h-48 object-cover rounded-lg mb-3"
                  />
                )}

                {/* Helpful Button & Reply Button */}
                <div className="flex gap-4">
                  <button
                    onClick={() => voteHelpful.mutate(r.id)}
                    disabled={voteHelpful.isPending || !user}
                    className="text-sm text-blue-600 hover:text-blue-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    👍 Helpful ({r.helpful_count})
                  </button>

                  {user && (
                    <button
                      onClick={() => setReplyingTo(r.id)}
                      className="text-sm text-gray-600 hover:text-gray-800 transition-colors"
                    >
                      💬 Reply
                    </button>
                  )}
                </div>

                {/* Reply Form */}
                {replyingTo === r.id && (
                  <div className="mt-4 ml-8 bg-gray-50 rounded-lg p-4">
                    <textarea
                      value={replyContent}
                      onChange={(e) => setReplyContent(e.target.value)}
                      placeholder="Write your reply..."
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 mb-2"
                    />
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleReplySubmit(r.id)}
                        disabled={createReply.isPending}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 text-sm"
                      >
                        {createReply.isPending ? 'Sending...' : 'Send Reply'}
                      </button>
                      <button
                        onClick={() => {
                          setReplyingTo(null);
                          setReplyContent("");
                        }}
                        className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors text-sm"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                )}

                {/* Replies */}
                {r.replies && r.replies.length > 0 && (
                  <div className="mt-4 ml-8 space-y-3">
                    {r.replies.map((reply) => (
                      <div key={reply.id} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <p className="font-semibold text-gray-900 text-sm">{reply.user}</p>
                          {reply.is_seller && (
                            <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                              Seller
                            </span>
                          )}
                          <span className="text-xs text-gray-500">
                            {new Date(reply.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-gray-700 text-sm">{reply.content}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <svg
              className="mx-auto h-16 w-16 text-gray-400 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z"
              />
            </svg>
            <p className="text-gray-600">No reviews yet. Be the first to review this product!</p>
            {user && (
              <button
                onClick={() => setShowReviewForm(true)}
                className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
              >
                Write a Review
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
}