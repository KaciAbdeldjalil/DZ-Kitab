import React, { useState, useEffect } from "react";
import { Link, useParams, useNavigate } from "react-router-dom";
import { CiHeart } from "react-icons/ci";
import { FaHeart } from "react-icons/fa";
import Header from "../components/header";
import Footer from "../components/footer";
import { booksData } from "../data/booksData";
import { useWishlist } from "../context/WishlistContext";
import "./BookDetails.css";

const BookDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [userRating, setUserRating] = useState(0);
  const { isInWishlist, toggleWishlist } = useWishlist();

  // Scroll to top when book ID changes
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [id]);

  // Find the book by ID
  const book = booksData.find((b) => b.id === parseInt(id));

  // If book not found, redirect or show error
  if (!book) {
    return (
      <div className="book-details-page">
        <Header />
        <div className="book-details-container">
          <p>Book not found</p>
          <Link to="/catalog" className="back-link">
            ← Back to Catalogue
          </Link>
        </div>
        <Footer />
      </div>
    );
  }

  // Get recommended books from the same domain
  const recommendedBooks = booksData
    .filter((b) => b.domain === book.domain && b.id !== book.id)
    .slice(0, 3);

  const renderStars = (rating, interactive = false, size = "medium") => {
    return (
      <div className={`stars stars-${size}`}>
        {[1, 2, 3, 4, 5].map((star) => (
          <span
            key={star}
            className={star <= rating ? "star filled" : "star"}
            onClick={interactive ? () => setUserRating(star) : undefined}
            style={interactive ? { cursor: "pointer" } : {}}
          >
            ★
          </span>
        ))}
      </div>
    );
  };

  return (
    <div className="book-details-page">
      <div className="book-details-container">
        {/* BACK LINK */}
        <Link to="/catalog" className="back-link">
          ← To Catalogue
        </Link>

        {/* MAIN BOOK DETAILS SECTION */}
        <div className="book-details-main">
          {/* LEFT COLUMN - IMAGE */}
          <div className="book-image-section">
            <img
              src={book.image}
              alt={book.title}
              className="book-detail-image"
            />
          </div>

          {/* RIGHT COLUMN - DETAILS */}
          <div className="book-info-section">
            <div className="book-header">
              <div className="title-rating-row">
                <h1 className="book-detail-title">{book.title}</h1>
                {renderStars(book.rating)}
              </div>
              <p className="book-author">by {book.author}</p>
            </div>

            <div className="book-metadata">
              <div className="metadata-item">
                <span className="metadata-label">Pages:</span>
                <span className="metadata-value">{book.pages}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Domain:</span>
                <span className="metadata-value">{book.domain}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Publication Year:</span>
                <span className="metadata-value">{book.year}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">ISBN:</span>
                <span className="metadata-value">{book.isbn}</span>
              </div>
              <div className="metadata-item">
                <span className="metadata-label">Status:</span>
                <span
                  className={`metadata-value status-${book.status.toLowerCase()}`}
                >
                  {book.status}
                </span>
              </div>
            </div>

            <div className="book-actions">
              <div className="price-rating-row">
                <div className="price-section">
                  <span className="book-detail-price">{book.price} DA</span>
                </div>
                <div className="add-rating">
                  <span className="add-rating-label">Add Rating:</span>
                  {renderStars(userRating, true, "small")}
                </div>
              </div>
              <div className="action-buttons">
                <button className="buy-now-btn-detail">Buy Now</button>
                <button
                  className="favorite-btn-detail"
                  onClick={() => toggleWishlist(book.id)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                  }}
                >
                  {isInWishlist(book.id) ? (
                    <FaHeart size={20} color="red" />
                  ) : (
                    <CiHeart size={24} color="black" />
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* DESCRIPTION SECTION */}
        <div className="book-description-section">
          <h2 className="section-title">Description</h2>
          <p className="description-text">{book.description}</p>
        </div>

        {/* ALSO RECOMMENDED SECTION */}
        <div className="recommended-section">
          <h2 className="section-title">Also Recommended</h2>
          <div className="recommended-grid">
            {recommendedBooks.map((recBook) => (
              <Link
                key={recBook.id}
                to={`/book/${recBook.id}`}
                className="recommended-card-link"
              >
                <div className="recommended-card">
                  <div className="recommended-image-wrapper">
                    <img
                      src={recBook.image}
                      alt={recBook.title}
                      className="recommended-image"
                    />
                  </div>
                  <div className="recommended-info">
                    <h4 className="recommended-title">{recBook.title}</h4>
                    {renderStars(recBook.rating, false, "small")}
                    <p className="recommended-price">{recBook.price} DA</p>
                    <button
                      className="recommended-buy-btn"
                      onClick={(e) => e.preventDefault()}
                    >
                      Buy now
                    </button>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BookDetails;
