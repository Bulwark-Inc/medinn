"use client";

import { useParams } from "next/navigation";
import { useProductBySlug } from "@/features/products/hooks/useProduct"; 
import { 
  useReviews, 
  useCreateReview, 
  useVoteHelpful // <--- FIX APPLIED HERE
} from "@/features/products/hooks/useReview";
import { useState } from "react";

export default function ProductDetail() {
  const params = useParams();
  const slug = params.slug; 

  const { 
    product, 
    isLoading,
    isError
  } = useProductBySlug(slug);

  const productId = product?.id; 

  // useReviews now uses the correct productId and conditional fetching
  const { data: reviews } = useReviews(productId, { enabled: !!productId });
  
  const createReview = useCreateReview();
  // Renamed the variable to match the hook name for clarity
  const voteHelpful = useVoteHelpful(); 
  const [review, setReview] = useState({ rating: 5, content: "" });

  // Handle Loading and Error States
  if (isLoading) {
    return <p>Loading product details...</p>;
  }

  if (isError || !product) {
    return <p>Error loading product, or product not found.</p>;
  }

  if (!product) return <p>Product not found.</p>;

  const handleReviewSubmit = (e) => {
    e.preventDefault();
    createReview.mutate({ product: product.id, ...review }); 
    setReview({ rating: 5, content: "" });
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-2">{product.name}</h1>
      <img src={product.image} alt={product.name} className="w-96 h-96 object-cover rounded" />
      <p className="text-lg mt-4">{product.description}</p>
      <p className="text-xl font-semibold mt-2">${product.price}</p>
      <p className="text-yellow-500">⭐ {product.average_rating || 0}</p>

      <hr className="my-6" />

      <h2 className="text-2xl font-bold mb-2">Reviews</h2>
      {reviews?.map((r) => (
        <div key={r.id} className="border rounded-lg p-3 mb-3">
          <p className="font-semibold">{r.user}</p>
          <p>⭐ {r.rating}</p>
          <p>{r.content}</p>
          <button
            // Call the correct mutation function
            onClick={() => voteHelpful.mutate(r.id)} 
            className="text-sm text-blue-500 hover:underline"
          >
            Helpful ({r.helpful_count})
          </button>
        </div>
      ))}

      <form onSubmit={handleReviewSubmit} className="mt-6 border-t pt-4">
        <h3 className="font-semibold mb-2">Leave a Review</h3>
        <input
          type="number"
          min="1"
          max="5"
          value={review.rating}
          onChange={(e) => setReview({ ...review, rating: e.target.value })}
          className="border px-2 py-1 rounded w-16 mb-2"
        />
        <textarea
          value={review.content}
          onChange={(e) => setReview({ ...review, content: e.target.value })}
          placeholder="Write your review..."
          className="border w-full p-2 rounded mb-2"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Submit Review
        </button>
      </form>
    </div>
  );
}